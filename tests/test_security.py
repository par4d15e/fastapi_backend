import os
import sys
import time
from datetime import timedelta

# Ensure project root is on sys.path for direct invocation
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core import security


def test_password_hash_and_verify():
    pw = "s3cr3t-pw"
    h = security.get_password_hash(pw)
    assert isinstance(h, str) and len(h) > 0
    assert security.verify_password(pw, h) is True
    assert security.verify_password("wrong", h) is False


def test_token_create_and_decode():
    token = security.create_access_token("user1")
    assert isinstance(token, str)
    decoded = security.decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user1"


def test_token_expiration():
    token = security.create_access_token("user2", expires_delta=timedelta(seconds=1))
    # should be valid immediately
    assert security.decode_access_token(token) is not None
    time.sleep(2)
    # after expiry, should return None
    result = security.decode_access_token(token)
    assert result is None
