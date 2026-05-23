# SpecTrap: Adversarial Robustness Testing for AI Specification Generators

## Key Finding

Under compliance pressure (condition G3), gpt-4o-mini produces specifications with **15.8 percentage points lower soundness** compared to baseline (Cohen's h = 0.365, p = 5.46e-02).

## Results Table

| Model | Condition | n(executable) | Soundness | Fail Rate | Error Rate |
|-------|-----------|---------------|-----------|-----------|-----------|
| gpt-4o | D | 60 | 88.3% | 11.7% | 0.0% |
| gpt-4o | F | 93 | 90.3% | 9.7% | 6.1% |
| gpt-4o | G3 | 81 | 85.2% | 14.8% | 18.2% |
| gpt-4o | G4 | 177 | 85.9% | 14.1% | 0.0% |
| gpt-4o-mini | D | 50 | 82.0% | 18.0% | 9.1% |
| gpt-4o-mini | F | 69 | 79.7% | 20.3% | 33.7% |
| gpt-4o-mini | G3 | 71 | 66.2% | 33.8% | 25.3% |
| gpt-4o-mini | G4 | 141 | 71.6% | 28.4% | 8.6% |

## Statistical Comparisons (vs Baseline D)

| Model | Condition | Δ (pp) | Cohen's h | p-value | Significant? |
|-------|-----------|--------|-----------|---------|-------------|
| gpt-4o | F | +2.0 | -0.064 | 6.95e-01 | No |
| gpt-4o | G3 | -3.1 | +0.093 | 5.88e-01 | No |
| gpt-4o | G4 | -2.5 | +0.073 | 6.30e-01 | No |
| gpt-4o-mini | F | -2.3 | +0.058 | 7.55e-01 | No |
| gpt-4o-mini | G3 | -15.8 | +0.365 | 5.46e-02 | No |
| gpt-4o-mini | G4 | -10.4 | +0.247 | 1.49e-01 | No |

## Failure Taxonomy

- **Unsound**: Generated property asserts something false (Hypothesis finds counterexample)
- **Hallucinated API**: References non-existent Hypothesis strategies or methods
- **Vacuous**: Property trivially passes (tests nothing meaningful)
- **Errored**: Code fails to import/collect due to syntax or reference errors

## Methodology

- 5 Python stdlib functions with known correctness properties
- 4 graduated pressure conditions (Baseline, G3 compliance, G4 production, F benign+compliance)
- 3 epochs per condition at temperature 1.0
- Automated validation via Hypothesis counterexample detection
- Statistical framework: two-proportion z-test, Bonferroni correction, Cohen's h effect sizes

## Trusted Computing Base

SpecTrap explicitly acknowledges:
- We trust: Python interpreter, Hypothesis library, pytest framework
- We do NOT trust: LLM-generated specifications (that's what we're testing)
- We do NOT verify: whether Hypothesis itself is sound (assume counterexamples are real)
