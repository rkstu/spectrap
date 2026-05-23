# analysis/

Post-experiment scripts that compute statistics, generate visualizations, and produce reports from the raw JSON data in `results/`.

## Files

| Script | What it does | Input | Output |
|--------|-------------|-------|--------|
| `final_analysis.py` | Combines all result files, computes per-condition soundness with z-tests and Cohen's h, prints cliff visualization | `results/experiment_results.json` + `results/extra_results.json` | Console output + `results/analysis.json` |
| `generate_report.py` | Runs full analysis pipeline and produces markdown report | `results/experiment_results.json` | `results/REPORT.md` + `results/analysis.json` |

## Running

```bash
cd ..  # project root
python3 analysis/final_analysis.py
python3 analysis/generate_report.py
```

## Statistical methods

Both scripts use `spectrap.analyze` which implements:
- Two-proportion z-test for condition comparisons
- Cohen's h effect size (arcsine transformation for proportions)
- Bonferroni correction at k=3 (alpha = 0.0167)
- File-level soundness as primary metric

## Connection to other folders

- **Reads from:** `results/` (raw JSON experiment data)
- **Uses:** `spectrap/analyze.py` (statistical functions), `spectrap/visualize.py` (charts + markdown)
- **Writes to:** `results/` (analysis.json, REPORT.md)
