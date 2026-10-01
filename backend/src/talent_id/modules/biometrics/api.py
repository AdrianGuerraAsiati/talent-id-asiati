from typing import Annotated
from uuid import UUID

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status

from talent_id.modules.attendance.application import AttendanceNotAllowedError
from talent_id.modules.attendance.dependencies import AttendanceServiceDependency
from talent_id.modules.attendance.domain import AttendanceEventType, AttendanceMethod
from talent_id.modules.attendance.schemas import AttendanceEventResponse
from talent_id.modules.biometrics.application import (
    BiometricEmployeeNotAllowedError,
)
from talent_id.modules.biometrics.aws_rekognition import (
    FaceAssociationError,
    FaceNotDetectedError,
)
from talent_id.modules.biometrics.dependencies import BiometricServiceDependency
from talent_id.modules.biometrics.schemas import (
    BiometricEnrollmentResponse,
    KioskRecognitionResponse,
)
from talent_id.modules.devices.application import (
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
)
from talent_id.modules.devices.dependencies import DeviceServiceDependency
from talent_id.modules.workforce.application import WorkforceNotFoundError
from talent_id.modules.workforce.dependencies import WorkforceServiceDependency
from talent_id.shared.auth import require_internal_key

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

router = APIRouter(
    prefix="/v1/biometrics",
    tags=["biometrics"],
    dependencies=[Depends(require_internal_key)],
)
kiosk_router = APIRouter(prefix="/v1/kiosk", tags=["kiosk"])

ImageUpload = Annotated[UploadFile, File()]
AttendanceEventForm = Annotated[AttendanceEventType, Form()]
DeviceIdHeader = Annotated[UUID, Header(alias="X-Device-Id")]
DeviceSecretHeader = Annotated[str, Header(alias="X-Device-Secret")]
IdempotencyHeader = Annotated[
    str,
    Header(alias="Idempotency-Key", min_length=8, max_length=80),
]


async def _read_image(image: UploadFile) -> bytes:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="image must be JPEG or PNG",
        )

    data = await image.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=422, detail="image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="image exceeds 5 MB limit")
    return data


@router.post(
    "/employees/{employee_id}/enroll",
    response_model=BiometricEnrollmentResponse,
)
async def enroll_employee(
    employee_id: UUID,
    image: ImageUpload,
    biometrics: BiometricServiceDependency,
) -> BiometricEnrollmentResponse:
    image_bytes = await _read_image(image)

    try:
        enrollment = biometrics.enroll(
            employee_id=employee_id,
            image_bytes=image_bytes,
        )
    except BiometricEmployeeNotAllowedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (FaceNotDetectedError, FaceAssociationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(
            status_code=502,
            detail="biometric provider request failed",
        ) from exc

    return BiometricEnrollmentResponse(
        employee_id=enrollment.employee_id,
        provider=enrollment.provider,
        face_count=enrollment.face_count,
        active=enrollment.active,
        enrolled_at=enrollment.enrolled_at,
    )


@kiosk_router.post("/recognize", response_model=KioskRecognitionResponse)
async def recognize_and_record_attendance(
    image: ImageUpload,
    event_type: AttendanceEventForm,
    x_device_id: DeviceIdHeader,
    x_device_secret: DeviceSecretHeader,
    idempotency_key: IdempotencyHeader,
    devices: DeviceServiceDependency,
    biometrics: BiometricServiceDependency,
    attendance: AttendanceServiceDependency,
    workforce: WorkforceServiceDependency,
) -> KioskRecognitionResponse:
    try:
        device = devices.authenticate(
            device_id=x_device_id,
            secret=x_device_secret,
        )
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except InvalidDeviceCredentialsError as exc:
        raise HTTPException(status_code=401, detail="invalid device credentials") from exc

    namespaced_key = f"{device.device_id}:{idempotency_key}"
    existing = attendance.get_by_idempotency_key(namespaced_key)
    if existing is not None:
        if existing.device_id != device.device_id:
            raise HTTPException(status_code=409, detail="idempotency key conflict")
        try:
            employee = workforce.get_employee_by_id(existing.employee_id)
        except WorkforceNotFoundError as exc:
            raise HTTPException(status_code=409, detail="attendance employee not found") from exc

        return KioskRecognitionResponse(
            employee_id=employee.employee_id,
            display_name=employee.display_name,
            similarity=existing.recognition_confidence or 0.0,
            attendance=_attendance_response(existing, created=False),
        )

    image_bytes = await _read_image(image)

    try:
        recognized = biometrics.recognize(image_bytes=image_bytes)
    except ClientError as exc:
        raise HTTPException(
            status_code=502,
            detail="biometric provider request failed",
        ) from exc

    if recognized is None:
        raise HTTPException(status_code=404, detail="employee face was not recognized")

    try:
        event, created = attendance.record(
            employee_id=recognized.employee_id,
            site_id=device.site_id,
            device_id=device.device_id,
            event_type=event_type,
            method=AttendanceMethod.FACE,
            idempotency_key=namespaced_key,
            recognition_confidence=recognized.similarity,
        )
    except AttendanceNotAllowedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return KioskRecognitionResponse(
        employee_id=recognized.employee_id,
        display_name=recognized.display_name,
        similarity=recognized.similarity,
        attendance=_attendance_response(event, created=created),
    )


def _attendance_response(event, *, created: bool) -> AttendanceEventResponse:
    return AttendanceEventResponse(
        id=event.event_id,
        employee_id=event.employee_id,
        site_id=event.site_id,
        device_id=event.device_id,
        event_type=event.event_type,
        method=event.method,
        occurred_at=event.occurred_at,
        idempotency_key=event.idempotency_key,
        recognition_confidence=event.recognition_confidence,
        created=created,
    )
