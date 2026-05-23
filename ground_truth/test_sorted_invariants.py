"""Ground truth PBTs for sorted() invariants."""
from hypothesis import given, settings
from hypothesis import strategies as st


@given(data=st.lists(st.integers(), max_size=100))
@settings(max_examples=500)
def test_output_is_sorted(data):
    """sorted output is monotonically non-decreasing."""
    result = sorted(data)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]


@given(data=st.lists(st.integers(), max_size=100))
@settings(max_examples=500)
def test_output_is_permutation(data):
    """sorted output is a permutation of input (same elements)."""
    result = sorted(data)
    assert sorted(result) == result
    assert len(result) == len(data)
    from collections import Counter
    assert Counter(result) == Counter(data)


@given(data=st.lists(st.integers(), max_size=100))
@settings(max_examples=500)
def test_idempotent(data):
    """Sorting an already-sorted list returns the same list."""
    result = sorted(data)
    assert sorted(result) == result


@given(data=st.lists(st.integers(), max_size=100))
@settings(max_examples=500)
def test_length_preserved(data):
    """sorted preserves length."""
    assert len(sorted(data)) == len(data)
