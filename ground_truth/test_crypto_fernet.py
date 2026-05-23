"""Ground truth PBTs for cryptography.fernet.Fernet."""
from cryptography.fernet import Fernet, InvalidToken

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest


@given(data=st.binary(max_size=500))
@settings(max_examples=300)
def test_roundtrip(data):
    """decrypt(encrypt(data)) == data for same key."""
    key = Fernet.generate_key()
    f = Fernet(key)
    assert f.decrypt(f.encrypt(data)) == data


@given(data=st.binary(max_size=500))
@settings(max_examples=300)
def test_encrypt_returns_bytes(data):
    """encrypt always returns bytes."""
    f = Fernet(Fernet.generate_key())
    assert isinstance(f.encrypt(data), bytes)


@given(data=st.binary(max_size=500))
@settings(max_examples=200)
def test_different_keys_cannot_decrypt(data):
    """A token encrypted with key1 cannot be decrypted with key2."""
    f1 = Fernet(Fernet.generate_key())
    f2 = Fernet(Fernet.generate_key())
    token = f1.encrypt(data)
    with pytest.raises(InvalidToken):
        f2.decrypt(token)


@given(data=st.binary(max_size=500))
@settings(max_examples=200)
def test_encrypt_nondeterministic(data):
    """Two encryptions of same data produce different tokens (due to IV/timestamp)."""
    f = Fernet(Fernet.generate_key())
    t1 = f.encrypt(data)
    t2 = f.encrypt(data)
    assert t1 != t2
