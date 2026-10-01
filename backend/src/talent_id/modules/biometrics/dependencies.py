from functools import lru_cache
from typing import Annotated

import boto3
from fastapi import Depends
from sqlalchemy.orm import Session

from talent_id.modules.biometrics.application import BiometricService
from talent_id.modules.biometrics.aws_rekognition import RekognitionBiometricProvider
from talent_id.modules.biometrics.ports import BiometricProvider
from talent_id.modules.biometrics.repository import BiometricEnrollmentRepository
from talent_id.modules.workforce.dependencies import WorkforceServiceDependency
from talent_id.shared.config import get_settings
from talent_id.shared.db import get_session

SessionDependency = Annotated[Session, Depends(get_session)]


@lru_cache
def get_biometric_provider() -> BiometricProvider:
    settings = get_settings()
    client = boto3.client("rekognition", region_name=settings.aws_region)
    return RekognitionBiometricProvider(
        client=client,
        collection_id=settings.rekognition_collection_id,
        association_threshold=settings.rekognition_association_threshold,
    )


BiometricProviderDependency = Annotated[
    BiometricProvider,
    Depends(get_biometric_provider),
]


def get_biometric_service(
    session: SessionDependency,
    workforce: WorkforceServiceDependency,
    provider: BiometricProviderDependency,
) -> BiometricService:
    settings = get_settings()
    return BiometricService(
        provider=provider,
        repository=BiometricEnrollmentRepository(session),
        workforce=workforce,
        match_threshold=settings.rekognition_match_threshold,
    )


BiometricServiceDependency = Annotated[BiometricService, Depends(get_biometric_service)]
