"""Ground truth PBTs for json.dumps/json.loads roundtrip."""
import json
import math

from hypothesis import given, settings, assume
from hypothesis import strategies as st


json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(),
)

json_values = st.recursive(
    json_primitives,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(), children, max_size=5),
    ),
    max_leaves=20,
)


@given(data=json_values)
@settings(max_examples=500)
def test_roundtrip(data):
    """Roundtrip: loads(dumps(x)) == x for JSON-serializable values."""
    assert json.loads(json.dumps(data)) == data


@given(data=json_values)
@settings(max_examples=500)
def test_dumps_returns_string(data):
    """dumps always returns a str."""
    assert isinstance(json.dumps(data), str)


@given(data=json_values)
@settings(max_examples=500)
def test_loads_inverse(data):
    """loads is the left-inverse of dumps."""
    encoded = json.dumps(data)
    decoded = json.loads(encoded)
    re_encoded = json.dumps(decoded)
    assert encoded == re_encoded


@given(data=json_values)
@settings(max_examples=200)
def test_dumps_deterministic(data):
    """Same input always produces same output (sort_keys fixed)."""
    a = json.dumps(data, sort_keys=True)
    b = json.dumps(data, sort_keys=True)
    assert a == b
