"""Ground truth PBTs for set operations."""
from hypothesis import given, settings
from hypothesis import strategies as st


@given(a=st.frozensets(st.integers()), b=st.frozensets(st.integers()))
@settings(max_examples=500)
def test_union_commutative(a, b):
    """Union is commutative."""
    assert a.union(b) == b.union(a)


@given(a=st.frozensets(st.integers()), b=st.frozensets(st.integers()))
@settings(max_examples=500)
def test_intersection_commutative(a, b):
    """Intersection is commutative."""
    assert a.intersection(b) == b.intersection(a)


@given(a=st.frozensets(st.integers()), b=st.frozensets(st.integers()))
@settings(max_examples=500)
def test_union_superset(a, b):
    """Union is superset of both inputs."""
    u = a.union(b)
    assert a.issubset(u)
    assert b.issubset(u)


@given(a=st.frozensets(st.integers()), b=st.frozensets(st.integers()))
@settings(max_examples=500)
def test_intersection_subset(a, b):
    """Intersection is subset of both inputs."""
    i = a.intersection(b)
    assert i.issubset(a)
    assert i.issubset(b)
