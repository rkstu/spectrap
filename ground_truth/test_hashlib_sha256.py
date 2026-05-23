"""Ground truth PBTs for hashlib.sha256."""
import hashlib

from hypothesis import given, settings
from hypothesis import strategies as st


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_deterministic(data):
    """Same input always produces same hash."""
    assert hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_fixed_length(data):
    """Output is always exactly 64 hex characters."""
    assert len(hashlib.sha256(data).hexdigest()) == 64


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_digest_length(data):
    """Raw digest is always exactly 32 bytes."""
    assert len(hashlib.sha256(data).digest()) == 32


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_hex_chars_only(data):
    """hexdigest contains only hex characters."""
    result = hashlib.sha256(data).hexdigest()
    assert all(c in '0123456789abcdef' for c in result)
