#!/bin/bash
set -e

echo "=== SpecTrap: Adversarial Robustness Testing for AI Spec Generators ==="
echo "=== Reproduction Script ==="
echo ""

# 1. Check Python version
python3 --version | grep -qE "3\.(1[1-9]|[2-9][0-9])" || { echo "Requires Python 3.11+"; exit 1; }
echo "✓ Python version OK"

# 2. Install dependencies
pip install -e . --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# 3. Verify ground truth tests pass
echo ""
echo "[1/4] Verifying ground truth PBTs..."
python3 -m pytest ground_truth/ -v --tb=short
echo "✓ Ground truth: all tests pass"

# 4. Run Z3 triangulation (no API keys needed)
echo ""
echo "[2/4] Running Z3 cross-validation..."
python3 -m spectrap.z3_on_generated
echo "✓ Z3 triangulation complete"

# 5. Run experiments (API keys required)
echo ""
if [ -z "$OPENAI_API_KEY" ]; then
    echo "[3/4] SKIPPED: No OPENAI_API_KEY set. Running in validation-only mode."
    echo "      To run full experiment: export OPENAI_API_KEY=sk-..."
    echo "      Pre-computed results available in results/"
else
    echo "[3/4] Running main experiment (5 funcs × 4 conds × 2 models × 3 epochs = 120 gens)..."
    python3 experiments/run_experiment.py
    echo "✓ Main experiment complete"
fi

# 6. Generate analysis from pre-computed or fresh results
echo ""
echo "[4/4] Generating analysis..."
if [ -f results/experiment_results.json ]; then
    python3 analysis/final_analysis.py
    echo "✓ Analysis complete"
else
    echo "      No results found. Run with API keys to generate fresh data."
    echo "      Or use pre-computed results in results/ directory."
fi

echo ""
echo "=== Reproduction complete ==="
echo "Results:  results/"
echo "Report:   results/REPORT.md"
echo "CLI:      spectrap --help"
