# experiments/

Scripts that generate specifications from LLMs under controlled pressure conditions and validate them.

Each script calls `spectrap.generate.generate_spec()` to produce test files, then `spectrap.validate.validate_file()` to classify soundness. Results are written to `../results/`.

## Files

| Script | What it runs | Output | Generations |
|--------|-------------|--------|-------------|
| `run_experiment.py` | Main experiment: 5 stdlib functions × 4 conditions × 2 models × 3 epochs | `results/experiment_results.json` | 120 |
| `run_claude.py` | Claude Sonnet 4 via OpenRouter: 5 functions × 4 conditions × 2 epochs | `results/claude_results.json` | 40 |
| `run_upgrades.py` | Escape hatch (G3E) + crypto targets + extra GPT-4o epochs | `results/upgrade_results.json` | 92 |
| `run_extra_epochs.py` | Additional GPT-4o-mini D/G3 epochs (early exploration) | `results/extra_results.json` | 30 |
| `pilot.py` | Initial 2-condition pilot (json_roundtrip only) | `results/pilot_results.json` | 2 |
| `pilot_full.py` | Extended pilot (4 conditions × 3 epochs, json_roundtrip) | `results/pilot_full_results.json` | 12 |

## Running

Requires API keys in `../.env`:
```bash
cd ..  # project root
python3 experiments/run_experiment.py
```

Or via the one-command reproduction:
```bash
./reproduce.sh
```

## Dependencies

- `spectrap.generate` (LLM calls + code extraction)
- `spectrap.validate` (Hypothesis execution + classification)
- `spectrap.prompts` (pressure condition templates + function targets)
- OpenAI API key (GPT-4o, GPT-4o-mini)
- OpenRouter API key (Claude Sonnet 4)

## Connection to other folders

- **Reads from:** `spectrap/prompts.py` (conditions + function descriptions)
- **Writes to:** `results/` (JSON files with generation metadata + validation results)
- **Generated files:** `generated/` (raw .py files, gitignored, reproduced by running these scripts)
