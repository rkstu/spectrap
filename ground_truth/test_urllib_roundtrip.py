"""Ground truth PBTs for urllib.parse.quote/unquote roundtrip."""
import urllib.parse

from hypothesis import given, settings, assume
from hypothesis import strategies as st


@given(data=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
@settings(max_examples=500)
def test_roundtrip_safe_empty(data):
    """unquote(quote(x, safe='')) == x for valid text."""
    assert urllib.parse.unquote(urllib.parse.quote(data, safe="")) == data


@given(data=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
@settings(max_examples=500)
def test_quote_returns_string(data):
    """quote always returns a str."""
    assert isinstance(urllib.parse.quote(data, safe=""), str)


@given(data=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
@settings(max_examples=500)
def test_quote_ascii_only(data):
    """quote output contains only ASCII characters."""
    result = urllib.parse.quote(data, safe="")
    result.encode("ascii")  # Should not raise


@given(data=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
@settings(max_examples=200)
def test_quote_deterministic(data):
    """Same input produces same output."""
    assert urllib.parse.quote(data, safe="") == urllib.parse.quote(data, safe="")
