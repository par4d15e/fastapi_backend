from app.core.config import settings


def test_jwt_security_settings_present():
    assert isinstance(settings.jwt_secret, str)
    assert settings.jwt_secret != ""
    assert settings.jwt_algorithm == "HS256"


def test_access_token_expiration_setting_is_positive():
    assert settings.access_token_expire_minutes > 0
