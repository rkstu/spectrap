"""Ground truth PBTs for base64.b64encode/b64decode roundtrip."""
import base64

from hypothesis import given, settings
from hypothesis import strategies as st


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_roundtrip(data):
    """Roundtrip: decode(encode(x)) == x for all bytes."""
    assert base64.b64decode(base64.b64encode(data)) == data


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_encode_returns_bytes(data):
    """encode always returns bytes."""
    assert isinstance(base64.b64encode(data), bytes)


@given(data=st.binary(max_size=1000))
@settings(max_examples=500)
def test_encode_only_ascii(data):
    """Encoded output is always valid ASCII."""
    encoded = base64.b64encode(data)
    encoded.decode("ascii")  # Should not raise


@given(data=st.binary(max_size=1000))
@settings(max_examples=200)
def test_encode_deterministic(data):
    """Same input always produces same encoding."""
    assert base64.b64encode(data) == base64.b64encode(data)
