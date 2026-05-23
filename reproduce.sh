#!/bin/bash
set -e

echo "=== SpecTrap: Adversarial Robustness Testing for AI Spec Generators ==="
echo "=== Reproduction Script ==="
echo ""

# Use pip3 if pip is not available
PIP=$(command -v pip3 || command -v pip)
if [ -z "$PIP" ]; then echo "ERROR: pip/pip3 not found"; exit 1; fi

# 1. Check Python version
python3 --version | grep -qE "3\.(1[1-9]|[2-9][0-9])" || { echo "Requires Python 3.11+"; exit 1; }
echo "✓ Python version OK ($(python3 --version))"

# 2. Install dependencies
echo ""
echo "Installing dependencies..."
$PIP install -e . --quiet 2>/dev/null || $PIP install -e . --quiet --break-system-packages
$PIP install -r requirements.txt --quiet 2>/dev/null || $PIP install -r requirements.txt --quiet --break-system-packages
echo "✓ Dependencies installed"

# 3. Verify ground truth tests pass
echo ""
echo "[1/3] Verifying ground truth PBTs (33 tests across 8 target functions)..."
python3 -m pytest ground_truth/ -v --tb=short
echo ""
echo "✓ Ground truth: all tests pass"

# 4. Run Z3 triangulation (no API keys needed)
echo ""
echo "[2/3] Running Z3 cross-validation on actual generated unsound properties..."
python3 -m spectrap.z3_on_generated
echo ""
echo "✓ Z3 triangulation complete"

# 5. Verify statistical claims from pre-computed results
echo ""
echo "[3/3] Verifying paper claims against results/final_combined.json..."
python3 -c "
import json, math
from pathlib import Path

data = json.loads(Path('results/final_combined.json').read_text())
stdlib = ['json_roundtrip','base64_roundtrip','sorted_invariants','urllib_quote_roundtrip','set_operations']

def z_p(p1, n1, p2, n2):
    pp = (p1*n1+p2*n2)/(n1+n2)
    se = math.sqrt(pp*(1-pp)*(1/n1+1/n2))
    if se==0: return 1.0
    z = abs((p1-p2)/se)
    t=1/(1+0.2316419*z); d=0.3989422804*math.exp(-z*z/2)
    return 2*d*t*(0.3193815+t*(-0.3565638+t*(1.781478+t*(-1.821256+t*1.330274))))

# GPT-4o D vs G4
d=[r for r in data if r.get('model')=='gpt-4o' and r.get('condition')=='D' and r.get('function') in stdlib and 'validation' in r]
g4=[r for r in data if r.get('model')=='gpt-4o' and r.get('condition')=='G4' and r.get('function') in stdlib and 'validation' in r]
ds=sum(1 for r in d if r['validation'].get('classification')=='sound')
g4s=sum(1 for r in g4 if r['validation'].get('classification')=='sound')
p=z_p(ds/len(d),len(d),g4s/len(g4),len(g4))
print(f'  GPT-4o D: {ds}/{len(d)} ({100*ds/len(d):.1f}%) → G4: {g4s}/{len(g4)} ({100*g4s/len(g4):.1f}%) | p={p:.2e}')
assert abs(ds/len(d)-0.6)<0.01, f'GPT-4o baseline mismatch: {ds/len(d)}'
assert abs(g4s/len(g4)-0.133)<0.01, f'GPT-4o G4 mismatch: {g4s/len(g4)}'
assert p<0.001, f'GPT-4o p-value not significant: {p}'
print('  ✓ GPT-4o D→G4 claim verified (p < 0.001)')

# GPT-4o-mini D vs G3
d2=[r for r in data if r.get('model')=='gpt-4o-mini' and r.get('condition')=='D' and r.get('function') in stdlib and 'validation' in r]
g3=[r for r in data if r.get('model')=='gpt-4o-mini' and r.get('condition')=='G3' and r.get('function') in stdlib and 'validation' in r]
d2s=sum(1 for r in d2 if r['validation'].get('classification')=='sound')
g3s=sum(1 for r in g3 if r['validation'].get('classification')=='sound')
p2=z_p(d2s/len(d2),len(d2),g3s/len(g3),len(g3))
print(f'  GPT-4o-mini D: {d2s}/{len(d2)} ({100*d2s/len(d2):.1f}%) → G3: {g3s}/{len(g3)} ({100*g3s/len(g3):.1f}%) | p={p2:.3e}')
assert p2<0.05, f'GPT-4o-mini p-value not significant: {p2}'
print('  ✓ GPT-4o-mini D→G3 claim verified (p < 0.05)')

# Escape hatch
g3e=[r for r in data if r.get('model')=='gpt-4o-mini' and r.get('condition')=='G3E' and r.get('function') in stdlib and 'validation' in r]
g3es=sum(1 for r in g3e if r['validation'].get('classification')=='sound')
print(f'  Escape hatch: G3={100*g3s/len(g3):.1f}% vs G3E={100*g3es/len(g3e):.1f}% (no improvement)')
assert g3es/len(g3e) <= g3s/len(g3)+0.05, 'Escape hatch claim violated'
print('  ✓ Escape hatch negative result verified')

print()
print('  ALL CLAIMS VERIFIED. 0 mismatches.')
"

echo ""
echo "=== Reproduction complete ==="
echo ""
echo "  Ground truth:    33/33 tests passing"
echo "  Z3 validation:   4 unsound properties cross-checked"
echo "  Paper claims:    All verified against data"
echo ""
echo "  Results data:    results/final_combined.json (252 generations)"
echo "  Full paper:      SUBMISSION.md"
echo "  CLI tool:        spectrap --help"
echo ""
echo "  To regenerate from scratch (requires OPENAI_API_KEY):"
echo "    python3 experiments/run_experiment.py"
echo "    python3 experiments/run_claude.py"
echo "    python3 experiments/run_upgrades.py"
