from typing import Any

from botocore.exceptions import ClientError

from talent_id.modules.biometrics.aws_rekognition import RekognitionBiometricProvider


class FakeRekognitionClient:
    def __init__(self, *, user_exists: bool = False) -> None:
        self.user_exists = user_exists
        self.deleted_faces: list[str] = []

    def create_user(self, **kwargs: Any) -> dict[str, Any]:
        if self.user_exists:
            raise ClientError(
                {
                    "Error": {
                        "Code": "ConflictException",
                        "Message": "user exists",
                    }
                },
                "CreateUser",
            )
        self.user_exists = True
        return {}

    def index_faces(self, **kwargs: Any) -> dict[str, Any]:
        return {"FaceRecords": [{"Face": {"FaceId": "face-001"}}]}

    def associate_faces(self, **kwargs: Any) -> dict[str, Any]:
        return {"AssociatedFaces": [{"FaceId": "face-001"}]}

    def search_users_by_image(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "UserMatches": [
                {
                    "Similarity": 99.7,
                    "User": {"UserId": "employee-uuid"},
                }
            ]
        }

    def delete_faces(self, **kwargs: Any) -> dict[str, Any]:
        self.deleted_faces.extend(kwargs["FaceIds"])
        return {}


def test_rekognition_provider_enrolls_existing_or_new_user() -> None:
    client = FakeRekognitionClient(user_exists=True)
    provider = RekognitionBiometricProvider(
        client=client,
        collection_id="employees",
        association_threshold=90,
    )

    result = provider.enroll(
        provider_user_id="employee-uuid",
        image_bytes=b"fake-image",
    )

    assert result.provider_user_id == "employee-uuid"
    assert result.face_ids == ("face-001",)


def test_rekognition_provider_returns_best_user_match() -> None:
    provider = RekognitionBiometricProvider(
        client=FakeRekognitionClient(),
        collection_id="employees",
        association_threshold=90,
    )

    match = provider.recognize(
        image_bytes=b"fake-image",
        threshold=98,
    )

    assert match is not None
    assert match.provider_user_id == "employee-uuid"
    assert match.similarity == 99.7
