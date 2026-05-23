# spectrap/

Core Python package. Installed via `pip install -e .` from the project root. Provides the `spectrap` CLI and all library functions.

## Modules

| Module | Purpose | Key functions |
|--------|---------|---------------|
| `__init__.py` | Package marker | |
| `prompts.py` | Pressure condition templates + target function descriptions | `CONDITIONS` dict, `FUNCTION_CONTEXT` dict |
| `generate.py` | Calls LLM APIs, extracts code from responses, saves to disk | `generate_spec()`, `extract_code()`, `run_pilot()` |
| `validate.py` | Runs generated test files via pytest+Hypothesis, classifies results | `validate_file()`, `validate_batch()`, `count_test_functions()` |
| `analyze.py` | Statistical analysis: z-tests, Cohen's h, Bonferroni correction | `analyze_results()`, `cohens_h()`, `two_proportion_z()`, `p_value_from_z()` |
| `visualize.py` | ASCII cliff charts + markdown report generation | `ascii_cliff_plot()`, `markdown_report()` |
| `cli.py` | CLI entry point: `spectrap run`, `spectrap report`, `spectrap validate` | `main()` |
| `z3_validator.py` | Theoretical Z3 reasoning about common property patterns | `z3_check_sorted_properties()`, `run_z3_triangulation()` |
| `z3_on_generated.py` | Z3 applied to actual unsound properties from experiments | `run_z3_on_generated()` |

## Architecture

```
User runs: spectrap run --functions X --models Y --conditions Z
    │
    ▼
generate.py: calls OpenAI/OpenRouter API → saves .py files
    │
    ▼
validate.py: runs pytest on each file → classifies sound/unsound/errored
    │
    ▼
analyze.py: computes per-condition statistics
    │
    ▼
visualize.py: produces ASCII charts + markdown report
```

## CLI usage

```bash
spectrap run --functions json_roundtrip,sorted_invariants --models gpt-4o-mini --conditions D,G3,G4 --epochs 3
spectrap report --results path/to/results.json
spectrap validate path/to/generated_test.py
```

## Adding a new target function

1. Add entry to `FUNCTION_CONTEXT` in `prompts.py` (name, description, signature, example)
2. Write ground truth tests in `ground_truth/test_<name>.py`
3. Run: `spectrap run --functions <key> --conditions all`

## Adding a new pressure condition

1. Add entry to `CONDITIONS` in `prompts.py` (name, pressure_level, user_template)
2. Run experiments with `--conditions <key>`

## Connection to other folders

- **Called by:** `experiments/` scripts (generation + validation), `analysis/` scripts (statistics)
- **Installed from:** `pyproject.toml` in project root
- **CLI registered at:** `pyproject.toml` → `[project.scripts]` → `spectrap = "spectrap.cli:main"`
