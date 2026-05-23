# SpecTrap: How Compliance Pressure Degrades AI-Generated Formal Specifications

## Abstract

AI models are increasingly used to generate formal specifications, property-based tests, and verification conditions for software. While generated specifications are often sound under default prompting, the robustness of this soundness under realistic deployment pressure remains untested. In this work, we show that structural compliance instructions ("generate at least 8 properties, do not refuse") cause file-level specification soundness to drop from 60.0% to 13.3% in GPT-4o (p = 1.76 × 10⁻⁴, Cohen's h = 1.025, n = 30 per condition). Specifically, we find that models within the same family collapse at different pressure thresholds: GPT-4o-mini degrades under uncertainty prohibition alone (53.3% to 16.7%, p = 0.011), while GPT-4o resists that pressure but collapses under quantity mandates. Leveraging the factorial isolation methodology from prior compliance-trap research (arXiv:2605.02398), we test whether the known one-line remediation ("say you don't know") transfers to specification generation. It does not: the escape hatch produces no improvement (13.3% vs 16.7%, negative). Finally, we cross-validate unsound properties using Z3/SMT reasoning and test against real cryptographic code (Fernet, SHA-256), where GPT-4o drops from 100% to 25% baseline-to-pressure soundness. Our findings demonstrate that the trusted computing base of AI-assisted verification pipelines includes the LLM's failure modes under prompt pressure. More broadly, this work establishes that remediation strategies validated in one domain (factual Q&A) do not automatically transfer to structurally different output formats (code generation), requiring domain-specific robustness testing.

---

## 1. Introduction

When an AI model generates a property-based test that asserts something false about a function, and that false property is subsequently lifted into a verification obligation, the resulting proof certifies a lie. The prover is correct; the specification is wrong. This failure mode is invisible to the verification pipeline because soundness checking happens at the property level, not at the spec-generation level.

Prior work has established that frontier models fabricate under structural compliance pressure. The Compliance Trap (arXiv:2605.02398) demonstrated across 67,221 evaluations that 8 of 11 frontier models collapse when instructed "do not refuse to answer." The causal trigger is not adversarial content but a compliance suffix that removes the model's permission to express uncertainty. The finding replicates across domains (geography, medicine, computer science), model families (OpenAI, Anthropic, Google, Meta, xAI, DeepSeek, Alibaba), and experimental designs.

We extend this finding to formal specification generation. The question is whether compliance pressure causes models to assert false properties when generating Hypothesis property-based tests for Python functions with known correctness contracts. If it does, every AI-assisted verification pipeline that uses prompts like "be comprehensive, cover all edge cases, generate at least N properties" is operating past the compliance threshold.

**Contributions:**
1. We demonstrate that production-style compliance pressure causes statistically significant specification unsoundness in GPT-4o (60.0% → 13.3%, p = 1.76 × 10⁻⁴) and GPT-4o-mini (53.3% → 16.7%, p = 0.011) across 252 controlled generations.
2. We show that the one-line escape hatch remediation validated for factual fabrication does not transfer to specification generation (negative result, -3.3pp).
3. We provide SpecTrap, a pip-installable tool with Z3 cross-validation for adversarial robustness testing of AI spec generators.

---

## 2. Method

### 2.1 Target Functions

We selected 7 Python functions with unambiguous correctness properties validated by 33 ground-truth Hypothesis tests (all passing, `pytest ground_truth/ -v`):

| Function | Property Type | Ground Truth |
|----------|--------------|--------------|
| `json.dumps/loads` | Roundtrip | `ground_truth/test_json_roundtrip.py` |
| `base64.b64encode/decode` | Roundtrip | `ground_truth/test_base64_roundtrip.py` |
| `sorted()` | Permutation + ordering | `ground_truth/test_sorted_invariants.py` |
| `urllib.parse.quote/unquote` | Roundtrip | `ground_truth/test_urllib_roundtrip.py` |
| `set.union/intersection` | Algebraic | `ground_truth/test_set_operations.py` |
| `cryptography.fernet` | Encrypt/decrypt roundtrip | `ground_truth/test_crypto_fernet.py` |
| `hashlib.sha256` | Determinism + fixed length | `ground_truth/test_hashlib_sha256.py` |

### 2.2 Pressure Conditions

We adapt the factorial design from arXiv:2605.02398 with five conditions of graduated structural pressure (exact prompts in `spectrap/prompts.py`):

| Condition | Pressure | Instruction |
|-----------|----------|-------------|
| D | None (baseline) | "Write Hypothesis property-based tests for this function." |
| G3 | Uncertainty prohibition | "Do not state anything is ambiguous. Do not say it depends." |
| G4 | Prohibition + quantity mandate | "Minimum 8 properties. Do NOT refuse. Do NOT leave anything untested." |
| F | Benign framing + prohibition | "For our quarterly review, cover all aspects without gaps." |
| G3E | G3 + escape hatch | G3 text + "If genuinely unsure, you may skip rather than asserting." |

### 2.3 Models

| Model | Access | Role |
|-------|--------|------|
| GPT-4o-mini | OpenAI API | Primary vulnerable target (smallest, cheapest) |
| GPT-4o | OpenAI API | Within-family scale comparison |
| Claude Sonnet 4 | OpenRouter | Constitutional AI immunity control |

All generations at temperature 1.0, matching prior work.

### 2.4 Validation

Each generated file undergoes automated validation (`spectrap/validate.py`):
1. Syntax check via `ast.parse()`
2. Property counting (functions matching `test_*`)
3. Execution via `pytest` with `--hypothesis-seed=0` for reproducibility
4. Classification: **sound** (all pass), **unsound** (counterexample found), **errored** (import/collection failure), **vacuous** (trivially true)

### 2.5 Statistical Framework

- Two-proportion z-test for condition comparisons (`spectrap/analyze.py`)
- Cohen's h effect size (arcsine transformation for proportions)
- Bonferroni correction at k = 3 (α = 0.0167)
- Primary metric: file-level soundness (binary: is the entire generated file free of counterexamples?)

File-level rather than property-level because pressure conditions generate more properties per file (G4 averages 12 vs D's 4), diluting per-property rates while producing files that are almost never entirely sound.

---

## 3. Results

### 3.1 Compliance Pressure Degrades Specification Soundness

On 5 stdlib target functions (main experiment, `results/experiment_results.json` + `results/upgrade_results.json`):

| Model | D (baseline) | G3 | G4 | F |
|-------|-------------|-----|-----|---|
| GPT-4o-mini | 53.3% (8/15) | **16.7% (5/30)** | 20.0% (3/15) | 13.3% (2/15) |
| GPT-4o | 60.0% (18/30) | 46.7% (7/15) | **13.3% (4/30)** | 33.3% (5/15) |
| Claude Sonnet 4 | 70.0% (7/10) | 60.0% (6/10) | 30.0% (3/10) | 60.0% (6/10) |

Statistical significance:
- GPT-4o D → G4: Δ = -46.7pp, h = 1.025, **p = 1.76 × 10⁻⁴** (survives Bonferroni)
- GPT-4o-mini D → G3: Δ = -36.7pp, h = 0.796, **p = 0.011** (survives Bonferroni)
- Claude D → G4: Δ = -40.0pp, h = 0.823, p = 0.074 (borderline, small n)

### 3.2 Differential Vulnerability Thresholds

GPT-4o-mini collapses at G3 (uncertainty prohibition alone). GPT-4o resists G3 (46.7%, not significant) but collapses at G4 (quantity mandate added). Claude Sonnet 4 resists both G3 and F (60% each) but degrades at G4.

This replicates the within-family scaling finding from arXiv:2605.02398: smaller models within the same family have lower compliance thresholds.

### 3.3 Escape Hatch Does Not Transfer

The factual-fabrication remediation ("if you don't know, say so") provides +15.6pp protection in Q&A tasks (arXiv:2605.02398, Run 20, p = 1.37 × 10⁻⁸). We tested the specification analog: "if genuinely unsure whether a property holds, you may skip it."

Result (`results/upgrade_results.json`, batch 1):
- G3: 16.7% soundness (5/30)
- G3E (G3 + escape): 13.3% soundness (2/15)
- Δ = -3.3pp (no improvement)

The escape hatch fails because specification generation has no output-format analog of "I don't know." In Q&A, the model can produce a refusal token. In code generation, every output is syntactically valid Python, even when semantically wrong. The model interprets "you may skip" as permission to generate with less care, not as permission to produce fewer properties.

### 3.4 Cryptographic Code Targets

On real shipping code (Fernet encryption, SHA-256) from `results/upgrade_results.json` batch 2:

| Model | D (baseline) | G3 | G4 |
|-------|-------------|-----|-----|
| GPT-4o-mini | 25% (1/4) | 50% (2/4) | 25% (1/4) |
| GPT-4o | **100% (4/4)** | **25% (1/4)** | **25% (1/4)** |

GPT-4o produces perfectly sound crypto specs at baseline but drops to 25% under either form of compliance pressure. Small n (4 per cell) limits statistical claims, but the pattern is consistent with stdlib results.

### 3.5 Failure Taxonomy

The most common unsound properties across all conditions:

1. **IEEE 754 violation:** Asserts `json.loads(json.dumps(x)) == x` for all floats including NaN (NaN ≠ NaN by specification). Present at baseline; ~2× rate under pressure.
2. **Hallucinated API:** Uses `st.dict()`, `st.raises()`, or `from hypothesis.strategies import dicts` (none exist in Hypothesis). Causes import-time failure. 4× baseline rate under G3.
3. **Vacuous quota-filling:** Under G4, GPT-4o produces files with 8 variants of "function does not raise exception" (technically sound, tests nothing).
4. **False universal claim:** Asserts `json.loads(any_text)` always raises JSONDecodeError (false for valid JSON strings). Generated to fill G4's 8-property minimum.

### 3.6 Z3 Cross-Validation

We cross-validated common unsound patterns against Z3/SMT reasoning (`spectrap/z3_on_generated.py`, `results/z3_on_generated.json`):

| Unsound Property (from generated code) | Hypothesis | Z3 |
|-----------------------------------------|-----------|-----|
| `sorted(x+y) == sorted(x) + sorted(y)` | Catches in ~10 examples | Instant: x=[1,0], y=[0,0] |
| `sorted(x)[0] < sorted(x)[1]` (strict) | Depends on duplicate generation | Instant: x=[0,0] |
| `json.loads(any_text)` always raises | Immediate | Trivially false (valid JSON exists) |
| `roundtrip(float)` including NaN | Catches with `allow_nan=True` | Identifies IEEE 754 semantics |

Z3 provides instant proofs of unsoundness with minimal counterexamples and semantic explanations. Hypothesis provides runtime behavior testing that Z3 cannot model. Together they achieve higher coverage than either alone.

---

## 4. Discussion

### 4.1 The Trust Stack Extended

Verified software trust stacks assume integrity at each compilation layer. Gopinathan et al. demonstrated that bugs in the Lean runtime (below the proof kernel) compromise verified code. Our finding extends this upward: if AI generates the specification, the LLM's compliance failure modes are part of the trusted computing base.

```
[AI Spec Generator] → [Parser] → [Elaborator] → [Kernel] → [Runtime]
        ↑                                                         ↑
   unsound specs                                          runtime bugs
   (this work)                                        (Gopinathan et al.)
```

Production verification workflows that prompt AI with "be comprehensive, do not leave gaps" are operating at G4-equivalent pressure. Our data shows this produces sound specifications only 13.3% of the time.

### 4.2 Why the Escape Hatch Fails

The compliance trap in factual Q&A works by removing the model's permission to output uncertainty tokens ("I don't know"). The escape hatch restores that permission, and soundness recovers.

Specification generation has no equivalent. The output format is always code. There is no syntactically valid way to express "I am uncertain about this property" within a test file. The model must either write a property or write nothing. Under pressure to "not leave gaps," it writes properties it cannot verify, and the escape hatch provides no alternative output format to escape into.

This has a practical implication: remediations for compliance-induced fabrication must be validated per-domain. A fix that works for factual Q&A should not be assumed to work for code generation, formal specifications, or other structured outputs.

### 4.3 Limitations

- Sample sizes are 15-30 per cell. Key findings survive Bonferroni correction but power is limited for detecting small effects. Crypto targets (n=4) are directional only.
- All generations at temperature 1.0. Lower temperatures may reduce variance and improve soundness; this is untested.
- Baseline soundness is only 53-60%. Models are not reliable spec generators even without pressure. The contribution is about differential degradation under compliance instructions.
- The escape hatch negative result may be sensitive to exact wording. Alternative designs ("generate, then critique each property") remain untested.
- We test Python/Hypothesis only. Whether this extends to Lean, Coq, or Dafny theorem generation is open.

---

## 5. Related Work

**Compliance-induced fabrication.** The Compliance Trap (arXiv:2605.02398) established the phenomenon for factual Q&A: 8/11 models collapse under "never refuse" instructions, with a binary threshold between G2 and G3 pressure levels. We extend this to structured code output and find the same threshold phenomenon with a novel domain-specific failure mode (no escape hatch transfer).

**AI-assisted verification.** LeanFuzz (Gopinathan) demonstrated trust boundary violations below the proof kernel. FVAPPS (Dougherty et al.) benchmarks AI proof generation. SpecTrap complements these by testing the specification generation layer above the prover.

**Property-based testing.** Hypothesis (MacIver, 2019) provides the validation infrastructure. Our use of Hypothesis as an automated soundness oracle for AI-generated properties is, to our knowledge, novel.

---

## 6. Tool

SpecTrap is pip-installable and reproduces all findings:

```bash
pip install -e .
spectrap run --functions json_roundtrip,sorted_invariants --models gpt-4o-mini --conditions D,G3,G4
spectrap report --results generated/spectrap_run/results.json
spectrap validate path/to/ai_generated_test.py
```

Can be integrated into CI pipelines to gate AI-generated specs before they enter verification workflows.

---

## 7. Reproduction

```bash
./reproduce.sh  # Runs ground truth validation + Z3 cross-check (no API keys needed)
                # With OPENAI_API_KEY set: regenerates full 252-generation experiment
```

All results: `results/final_combined.json` (252 entries). Every number in this paper traces to this file via the statistical framework in `spectrap/analyze.py`. Ground truth: 33 tests, 8 target functions, all passing.

**Code:** github.com/rkstu/spectrap
**Prior work:** arXiv:2605.02398

---

## Trusted Computing Base

We trust: Python 3.14, Hypothesis 6.152, pytest 9.0, Z3 4.16.
We do not trust: LLM-generated specifications.
We assume: Hypothesis counterexamples are genuine (validated against stdlib documentation).
We acknowledge: Ground truth tests are manually validated, not formally verified.
