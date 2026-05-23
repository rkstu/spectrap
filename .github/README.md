# .github/

GitHub Actions CI workflows for automated validation of AI-generated specifications.

## Workflows

| File | Trigger | What it does |
|------|---------|-------------|
| `workflows/spectrap-ci.yml` | Push to main, PRs | Runs ground truth tests, validates any generated specs in repo |
| `workflows/spectrap-gate.yml` | PRs touching `specs/`, `tests/generated/`, `properties/` | Validates AI-generated spec files, optionally re-generates under pressure |

## Usage

These workflows activate automatically when the repo is hosted on GitHub. `spectrap-gate.yml` is the production use case: teams add it to repositories where AI generates property-based tests, and it gates merges if specs are unsound.

## Connection to other folders

- **Uses:** `spectrap` package (installed via `pip install -e .`)
- **Validates:** `ground_truth/` tests + any files in `generated/`
