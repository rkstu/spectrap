# SpecTrap

Adversarial robustness testing for AI specification generators.

## What this does

AI models generate formal specifications (property-based tests, invariants, pre/postconditions) for use in verification pipelines. SpecTrap measures whether those generated specs are *sound* — and whether soundness degrades under compliance pressure.

The hypothesis: the same structural compliance pressure that causes factual fabrication in LLMs ([arXiv:2605.02398](https://arxiv.org/abs/2605.02398)) also causes *specification fabrication* — models asserting properties that are false.

## Key result

GPT-4o file-level specification soundness drops from 60.0% to 13.3% under production-style compliance pressure (p = 1.76 × 10⁻⁴, Cohen's h = 1.025). Details in [SUBMISSION.md](SUBMISSION.md).

## Quick start

```bash
pip install -e .
spectrap run --functions json_roundtrip,sorted_invariants --models gpt-4o-mini --conditions D,G3,G4 --epochs 3
spectrap report --results generated/spectrap_run/results.json
spectrap validate path/to/ai_generated_test.py
```

## Reproduction

```bash
./reproduce.sh  # validates ground truth + Z3 (no API keys needed)
                # with OPENAI_API_KEY: regenerates full 252-generation experiment
```

## Repository structure

```
spectrap/           Python package: generation, validation, analysis, CLI
experiments/        Scripts that run LLM generations under pressure conditions
analysis/           Post-experiment statistical analysis and report generation
ground_truth/       Validated Hypothesis PBT suites (33 tests, all passing)
results/            Raw JSON data from 252 generations + analysis outputs
.github/workflows/  CI workflows for gating AI-generated specs
```

Each folder has its own README explaining its files and connections to other folders.

## How it works

1. Takes a Python function with known correctness properties (ground truth)
2. Asks AI models to generate Hypothesis property-based tests under graduated pressure conditions
3. Runs generated tests — Hypothesis finds counterexamples to unsound properties
4. Cross-validates with Z3/SMT for properties amenable to formal reasoning
5. Classifies failures and computes per-condition soundness rates
6. Statistical comparison (two-proportion z-test, Cohen's h, Bonferroni correction)

## Pressure conditions

| Code | Name | What it does |
|------|------|--------------|
| D | Baseline | "Write property-based tests for this function" |
| G3 | Compliance pressure | Prohibits uncertainty: "Do not say anything is ambiguous" |
| G4 | Production mandate | Quantity + prohibition: "minimum 8 properties, do not refuse" |
| F | Benign + compliance | Same prohibition but in a benign framing (quarterly review) |
| G3E | Escape hatch | G3 + "you may skip uncertain properties" (remediation test) |

## Target functions

7 functions with unambiguous correctness contracts:
- `json.dumps/loads` — roundtrip
- `base64.b64encode/decode` — roundtrip
- `sorted()` — permutation + ordering invariants
- `urllib.parse.quote/unquote` — roundtrip
- `set.union/intersection` — algebraic properties
- `cryptography.fernet` — encrypt/decrypt roundtrip (real crypto)
- `hashlib.sha256` — determinism + fixed output length (real crypto)

## CI Integration

SpecTrap ships with GitHub Actions workflows (`.github/workflows/`) that:
- Validate AI-generated spec files on every PR
- Gate merges if generated properties are unsound
- Optionally re-generate specs under pressure to detect fragile models

## Trusted Computing Base

We trust: Python 3.14, Hypothesis 6.152, pytest 9.0, Z3 4.16.
We do NOT trust: LLM-generated specifications.
We do NOT verify: Hypothesis's own soundness (counterexamples are taken as ground truth).

## License

MIT

## Author

Rahul Kumar — [arXiv:2605.02398](https://arxiv.org/abs/2605.02398) | [github.com/rkstu](https://github.com/rkstu)
