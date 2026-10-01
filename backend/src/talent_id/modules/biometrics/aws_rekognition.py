from typing import Any
from uuid import uuid4

from botocore.exceptions import ClientError

from talent_id.modules.biometrics.domain import EnrollmentResult, RecognitionMatch


class FaceNotDetectedError(ValueError):
    pass


class FaceAssociationError(ValueError):
    pass


class RekognitionBiometricProvider:
    provider_name = "aws_rekognition"

    def __init__(
        self,
        *,
        client: Any,
        collection_id: str,
        association_threshold: float,
    ) -> None:
        self._client = client
        self._collection_id = collection_id
        self._association_threshold = association_threshold

    def enroll(self, *, provider_user_id: str, image_bytes: bytes) -> EnrollmentResult:
        self._ensure_user(provider_user_id)

        indexed = self._client.index_faces(
            CollectionId=self._collection_id,
            Image={"Bytes": image_bytes},
            MaxFaces=1,
            QualityFilter="AUTO",
            DetectionAttributes=[],
        )
        face_ids = tuple(
            record["Face"]["FaceId"]
            for record in indexed.get("FaceRecords", [])
            if record.get("Face", {}).get("FaceId")
        )
        if not face_ids:
            raise FaceNotDetectedError("no usable face was detected")

        association = self._client.associate_faces(
            CollectionId=self._collection_id,
            UserId=provider_user_id,
            FaceIds=list(face_ids),
            UserMatchThreshold=self._association_threshold,
            ClientRequestToken=uuid4().hex,
        )
        associated = tuple(
            face["FaceId"]
            for face in association.get("AssociatedFaces", [])
            if face.get("FaceId")
        )
        if len(associated) != len(face_ids):
            self._client.delete_faces(
                CollectionId=self._collection_id,
                FaceIds=list(face_ids),
            )
            raise FaceAssociationError("indexed face could not be associated with employee")

        return EnrollmentResult(
            provider_user_id=provider_user_id,
            face_ids=associated,
        )

    def recognize(
        self,
        *,
        image_bytes: bytes,
        threshold: float,
    ) -> RecognitionMatch | None:
        response = self._client.search_users_by_image(
            CollectionId=self._collection_id,
            Image={"Bytes": image_bytes},
            UserMatchThreshold=threshold,
            MaxUsers=1,
            QualityFilter="AUTO",
        )
        matches = response.get("UserMatches", [])
        if not matches:
            return None

        best = matches[0]
        provider_user_id = best.get("User", {}).get("UserId")
        similarity = best.get("Similarity")
        if provider_user_id is None or similarity is None:
            return None

        return RecognitionMatch(
            provider_user_id=str(provider_user_id),
            similarity=float(similarity),
        )

    def _ensure_user(self, provider_user_id: str) -> None:
        try:
            self._client.create_user(
                CollectionId=self._collection_id,
                UserId=provider_user_id,
                ClientRequestToken=uuid4().hex,
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "ConflictException":
                raise
