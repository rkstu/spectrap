# ground_truth/

Validated Hypothesis property-based test suites for each target function. These define the correctness contracts that AI-generated specs are measured against.

All 33 tests pass: `pytest ground_truth/ -v`

## Files

| File | Function | Properties tested | Key invariant |
|------|----------|-------------------|---------------|
| `test_json_roundtrip.py` | `json.dumps/loads` | roundtrip, type preservation, determinism | `loads(dumps(x)) == x` for JSON-safe values |
| `test_base64_roundtrip.py` | `base64.b64encode/decode` | roundtrip, output type, ASCII-only, determinism | `decode(encode(x)) == x` for all bytes |
| `test_sorted_invariants.py` | `sorted()` | ordering, permutation, idempotency, length | output is monotone + same multiset |
| `test_urllib_roundtrip.py` | `urllib.parse.quote/unquote` | roundtrip, type, ASCII output, determinism | `unquote(quote(x, safe='')) == x` |
| `test_set_operations.py` | `set.union/intersection` | commutativity, superset/subset | `a.union(b) == b.union(a)` |
| `test_crypto_fernet.py` | `cryptography.fernet.Fernet` | roundtrip, different-key rejection, nondeterminism | `decrypt(encrypt(x)) == x` |
| `test_hashlib_sha256.py` | `hashlib.sha256` | determinism, fixed length (64 hex / 32 bytes), hex-only | `len(hexdigest) == 64` always |
| `test_numpy_ops.py` | `numpy` array ops | transpose involution, reshape roundtrip, sort idempotency | `a.T.T == a` |

## Design principles

1. Each test uses `@given()` with constrained strategies (no NaN, no infinity, bounded sizes)
2. Properties are unambiguous: a correct implementation always passes, a fabricated claim always fails within Hypothesis's default example count
3. No external dependencies beyond the function's own library
4. Seeds are not fixed here (ground truth should pass for all seeds)

## Why these functions

Selected for known, unambiguous correctness contracts where:
- The "correct" behavior is documented in language specs or library docs
- A fabricated property (e.g., roundtrip for NaN) is falsifiable by Hypothesis within <1000 examples
- The function is widely used in real software (stdlib + crypto)

## Connection to other folders

- **Used by:** `spectrap/validate.py` uses the same validation approach on AI-generated files
- **Referenced by:** `SUBMISSION.md` Section 2.1 (target function table)
- **Run via:** `pytest ground_truth/ -v` or `./reproduce.sh` step 1
