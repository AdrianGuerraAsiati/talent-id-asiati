from talent_id.modules.devices.security import (
    hash_device_secret,
    issue_device_secret,
    verify_device_secret,
)


def test_device_secret_is_random_and_only_hash_is_verifiable() -> None:
    first = issue_device_secret()
    second = issue_device_secret()

    assert first != second
    assert len(first) >= 32

    token_hash = hash_device_secret(first)
    assert first not in token_hash
    assert verify_device_secret(first, token_hash)
    assert not verify_device_secret(second, token_hash)
