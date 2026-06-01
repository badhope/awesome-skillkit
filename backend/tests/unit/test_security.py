from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

settings = get_settings()


class TestPasswordHashing:

    def test_password_hashing_and_verification(self) -> None:
        plain_password = "MySecureP@ss1"
        hashed = get_password_hash(plain_password)

        assert hashed != plain_password
        assert hashed.startswith("$2b$")

        assert verify_password(plain_password, hashed) is True

    def test_password_verification_fails_with_wrong_password(self) -> None:
        plain_password = "MySecureP@ss1"
        hashed = get_password_hash(plain_password)

        assert verify_password("WrongPassword", hashed) is False

    def test_password_hashing_is_deterministic(self) -> None:
        plain_password = "MySecureP@ss1"
        hashed1 = get_password_hash(plain_password)
        hashed2 = get_password_hash(plain_password)

        assert hashed1 != hashed2
        assert verify_password(plain_password, hashed1) is True
        assert verify_password(plain_password, hashed2) is True

    def test_empty_password(self) -> None:
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_unicode_password(self) -> None:
        plain = "密码123!@#Test"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True


class TestJWTTokenCreation:

    def test_jwt_token_creation(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject)

        assert token is not None
        assert isinstance(token, str)
        parts = token.split(".")
        assert len(parts) == 3

    def test_jwt_token_contains_expected_claims(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == subject
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_jwt_token_with_custom_expiry(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        custom_delta = timedelta(hours=1)
        token = create_access_token(subject=subject, expires_delta=custom_delta)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        delta = exp - iat
        assert delta.total_seconds() == pytest.approx(3600, abs=5)

    def test_jwt_token_with_extra_claims(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        extra = {"role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(subject=subject, extra_claims=extra)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    def test_create_refresh_token(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        token = create_refresh_token(subject=subject)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == subject
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload


class TestJWTTokenVerification:

    def test_jwt_token_verification(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject)

        payload = decode_token(token)
        assert payload["sub"] == subject
        assert payload["type"] == "access"

    def test_expired_token_raises_error(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(subject=subject, expires_delta=expired_delta)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises_error(self) -> None:
        invalid_token = "this.is.not.a.valid.jwt.token"

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(invalid_token)
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises_error(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        token = create_access_token(subject=subject)
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".tampered_signature"

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered)
        assert exc_info.value.status_code == 401

    def test_token_with_wrong_secret(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        wrong_settings_token = jwt.encode(
            {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"},
            "wrong-secret-key",
            algorithm=settings.JWT_ALGORITHM,
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(wrong_settings_token)
        assert exc_info.value.status_code == 401

    def test_token_with_wrong_algorithm(self) -> None:
        subject = "a0000000-0000-0000-0000-000000000001"
        try:
            token = jwt.encode(
                {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"},
                settings.JWT_SECRET_KEY,
                algorithm="HS512",
            )
        except Exception:
            pytest.skip("HS512 not supported by jose")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_empty_token(self) -> None:
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_token("")
        assert exc_info.value.status_code == 401

    def test_token_without_subject(self) -> None:
        token = jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        payload = decode_token(token)
        assert payload.get("sub") is None