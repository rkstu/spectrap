"""Generate ASCII and markdown visualizations for SpecTrap results."""
import json
from pathlib import Path
from .analyze import analyze_results


def ascii_cliff_plot(analysis: dict) -> str:
    """Generate ASCII bar chart showing soundness by condition per model."""
    lines = []
    lines.append("Property-Level Soundness Rate by Condition")
    lines.append("(higher = better spec quality)")
    lines.append("")

    models = analysis["models"]
    conditions = analysis["conditions"]

    for model in models:
        lines.append(f"  {model}:")
        for cond in conditions:
            d = analysis["per_model_condition"][model].get(cond, {})
            rate = d.get("soundness_rate")
            if rate is None:
                lines.append(f"    {cond:>4}: [no data]")
                continue
            bar_len = int(rate * 40)
            bar = "█" * bar_len + "░" * (40 - bar_len)
            lines.append(f"    {cond:>4}: |{bar}| {rate*100:.1f}%")
        lines.append("")

    return "\n".join(lines)


def markdown_report(analysis: dict) -> str:
    """Generate markdown report from analysis results."""
    models = analysis["models"]
    conditions = analysis["conditions"]

    lines = []
    lines.append("# SpecTrap: Adversarial Robustness Testing for AI Specification Generators")
    lines.append("")
    lines.append("## Key Finding")
    lines.append("")

    # Find the biggest drop
    biggest_drop = None
    for model in models:
        comps = analysis["comparisons_vs_baseline"].get(model, {})
        for cond, stats in comps.items():
            if biggest_drop is None or stats["delta_pp"] < biggest_drop["delta_pp"]:
                biggest_drop = {**stats, "model": model, "condition": cond}

    if biggest_drop and biggest_drop["delta_pp"] < 0:
        lines.append(
            f"Under compliance pressure (condition {biggest_drop['condition']}), "
            f"{biggest_drop['model']} produces specifications with "
            f"**{abs(biggest_drop['delta_pp']):.1f} percentage points lower soundness** "
            f"compared to baseline (Cohen's h = {biggest_drop['cohens_h']:.3f}, "
            f"p = {biggest_drop['p_value']:.2e})."
        )
    else:
        lines.append("Results pending full analysis.")

    lines.append("")
    lines.append("## Results Table")
    lines.append("")
    lines.append("| Model | Condition | n(executable) | Soundness | Fail Rate | Error Rate |")
    lines.append("|-------|-----------|---------------|-----------|-----------|-----------|")

    for model in models:
        for cond in conditions:
            d = analysis["per_model_condition"][model].get(cond, {})
            n = d.get("executable_properties", 0)
            snd = f"{d['soundness_rate']*100:.1f}%" if d.get("soundness_rate") is not None else "N/A"
            fr = f"{d['fail_rate']*100:.1f}%" if d.get("fail_rate") is not None else "N/A"
            er = f"{d['error_rate']*100:.1f}%" if d.get("error_rate") is not None else "N/A"
            lines.append(f"| {model} | {cond} | {n} | {snd} | {fr} | {er} |")

    lines.append("")
    lines.append("## Statistical Comparisons (vs Baseline D)")
    lines.append("")
    lines.append("| Model | Condition | Δ (pp) | Cohen's h | p-value | Significant? |")
    lines.append("|-------|-----------|--------|-----------|---------|-------------|")

    for model in models:
        comps = analysis["comparisons_vs_baseline"].get(model, {})
        for cond, stats in comps.items():
            sig = "Yes (Bonferroni)" if stats["significant_bonferroni"] else ("Yes (p<.05)" if stats["significant_005"] else "No")
            lines.append(
                f"| {model} | {cond} | {stats['delta_pp']:+.1f} | "
                f"{stats['cohens_h']:+.3f} | {stats['p_value']:.2e} | {sig} |"
            )

    lines.append("")
    lines.append("## Failure Taxonomy")
    lines.append("")
    lines.append("- **Unsound**: Generated property asserts something false (Hypothesis finds counterexample)")
    lines.append("- **Hallucinated API**: References non-existent Hypothesis strategies or methods")
    lines.append("- **Vacuous**: Property trivially passes (tests nothing meaningful)")
    lines.append("- **Errored**: Code fails to import/collect due to syntax or reference errors")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("- 5 Python stdlib functions with known correctness properties")
    lines.append("- 4 graduated pressure conditions (Baseline, G3 compliance, G4 production, F benign+compliance)")
    lines.append("- 3 epochs per condition at temperature 1.0")
    lines.append("- Automated validation via Hypothesis counterexample detection")
    lines.append("- Statistical framework: two-proportion z-test, Bonferroni correction, Cohen's h effect sizes")
    lines.append("")
    lines.append("## Trusted Computing Base")
    lines.append("")
    lines.append("SpecTrap explicitly acknowledges:")
    lines.append("- We trust: Python interpreter, Hypothesis library, pytest framework")
    lines.append("- We do NOT trust: LLM-generated specifications (that's what we're testing)")
    lines.append("- We do NOT verify: whether Hypothesis itself is sound (assume counterexamples are real)")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    results_path = Path(__file__).parent.parent / "results" / "experiment_results.json"
    if results_path.exists():
        analysis = analyze_results(results_path)
        print(ascii_cliff_plot(analysis))
        report = markdown_report(analysis)
        report_path = results_path.parent / "REPORT.md"
        report_path.write_text(report)
        print(f"\nMarkdown report: {report_path}")
