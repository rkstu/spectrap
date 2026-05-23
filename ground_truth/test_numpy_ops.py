"""Ground truth PBTs for numpy operations — real ML infrastructure targets."""
import numpy as np
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays, array_shapes


float_arrays = arrays(
    dtype=np.float64,
    shape=array_shapes(min_dims=1, max_dims=2, min_side=1, max_side=10),
    elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
)


@given(a=float_arrays)
@settings(max_examples=300)
def test_transpose_involution(a):
    """Transposing twice returns the original array."""
    np.testing.assert_array_equal(a.T.T, a)


@given(a=float_arrays)
@settings(max_examples=300)
def test_reshape_roundtrip(a):
    """Reshape to flat and back preserves content."""
    flat = a.reshape(-1)
    back = flat.reshape(a.shape)
    np.testing.assert_array_equal(back, a)


@given(shape=array_shapes(min_dims=1, max_dims=2, min_side=1, max_side=10), data=st.data())
@settings(max_examples=300)
def test_addition_commutative(shape, data):
    """Element-wise addition is commutative for same-shape arrays."""
    elems = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    a = data.draw(arrays(dtype=np.float64, shape=shape, elements=elems))
    b = data.draw(arrays(dtype=np.float64, shape=shape, elements=elems))
    np.testing.assert_array_almost_equal(a + b, b + a)


@given(a=float_arrays)
@settings(max_examples=300)
def test_sort_idempotent(a):
    """Sorting along axis is idempotent."""
    sorted_once = np.sort(a, axis=-1)
    sorted_twice = np.sort(sorted_once, axis=-1)
    np.testing.assert_array_equal(sorted_once, sorted_twice)


@given(a=float_arrays)
@settings(max_examples=300)
def test_sum_axis_shape(a):
    """Summing along an axis reduces that dimension."""
    if a.ndim >= 1:
        result = np.sum(a, axis=0)
        expected_shape = a.shape[1:] if a.ndim > 1 else ()
        assert result.shape == expected_shape
