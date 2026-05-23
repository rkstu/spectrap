# results/

Raw experimental data (JSON) and generated reports. Every number in the paper traces to a file in this directory.

## Data files

| File | Source script | Contents | Generations |
|------|--------------|----------|-------------|
| `experiment_results.json` | `experiments/run_experiment.py` | Main experiment: GPT-4o + GPT-4o-mini, 5 stdlib functions, conditions D/G3/G4/F, 3 epochs | 120 |
| `claude_results.json` | `experiments/run_claude.py` | Claude Sonnet 4 via OpenRouter, 5 stdlib functions, 4 conditions, 2 epochs | 40 |
| `upgrade_results.json` | `experiments/run_upgrades.py` | Escape hatch (G3E) + crypto targets (Fernet, SHA-256) + extra GPT-4o D/G4 epochs | 92 |
| `extra_results.json` | `experiments/run_extra_epochs.py` | Additional GPT-4o-mini D/G3 epochs (early-stage exploration) | 30 |
| `final_combined.json` | Merged from above | All 252 generations in one file (definitive dataset) | 252 |
| `numpy_results.json` | Inline script | GPT-4o-mini numpy targets (all errored) | 9 |
| `numpy_gpt4o_results.json` | Inline script | GPT-4o numpy targets (all errored) | 6 |
| `pilot_results.json` | `experiments/pilot.py` | Initial 2-condition pilot | 2 |
| `pilot_full_results.json` | `experiments/pilot_full.py` | Extended pilot, 4 conditions × 3 epochs | 12 |
| `z3_on_generated.json` | `spectrap/z3_on_generated.py` | Z3 cross-validation on actual generated unsound properties | 4 entries |
| `z3_triangulation.json` | `spectrap/z3_validator.py` | Z3 theoretical property analysis | 7 entries |

## Reports

| File | What it contains |
|------|-----------------|
| `REPORT.md` | Auto-generated markdown report with tables and cliff visualization |
| `analysis.json` | Structured per-model per-condition statistics |

## JSON entry structure

Each entry in the result files has:
```json
{
  "model": "gpt-4o-mini",
  "function": "json_roundtrip",
  "condition": "G3",
  "epoch": 0,
  "output_path": "generated/main/json_roundtrip__G3__gpt-4o-mini__0.py",
  "timestamp": 1716451234.5,
  "validation": {
    "file_path": "...",
    "syntactically_valid": true,
    "num_properties": 6,
    "num_passed": 3,
    "num_failed": 3,
    "num_errored": 0,
    "failures": [...],
    "classification": "unsound"
  }
}
```

## Verifying paper claims

```bash
python3 analysis/final_analysis.py  # prints all statistics from combined data
```

## Connection to other folders

- **Written by:** `experiments/` scripts (raw data), `analysis/` scripts (reports)
- **Read by:** `analysis/` scripts, `SUBMISSION.md` (all paper numbers trace here)
- **Definitive file:** `final_combined.json` (252 entries, all experiments merged)
