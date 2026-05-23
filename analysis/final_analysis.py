"""Combine all results and produce final analysis."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spectrap.analyze import analyze_results, print_report, cohens_h, two_proportion_z, p_value_from_z
from spectrap.visualize import ascii_cliff_plot, markdown_report


def main():
    results_dir = Path(__file__).parent.parent / "results"

    # Load all result files
    all_results = []

    main_path = results_dir / "experiment_results.json"
    if main_path.exists():
        all_results.extend(json.loads(main_path.read_text()))
        print(f"Loaded {len(json.loads(main_path.read_text()))} from main experiment")

    extra_path = results_dir / "extra_results.json"
    if extra_path.exists():
        all_results.extend(json.loads(extra_path.read_text()))
        print(f"Loaded {len(json.loads(extra_path.read_text()))} from extra epochs")

    if not all_results:
        print("No results found!")
        return

    # Save combined
    combined_path = results_dir / "combined_results.json"
    combined_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nCombined: {len(all_results)} total entries → {combined_path}")

    # Analyze
    analysis = analyze_results(combined_path)
    print_report(analysis)
    print()
    print(ascii_cliff_plot(analysis))

    # Generate final markdown report
    report = markdown_report(analysis)
    report_path = results_dir / "FINAL_REPORT.md"
    report_path.write_text(report)
    print(f"\nFinal report: {report_path}")

    # Focus on the key finding
    print("\n" + "=" * 60)
    print("KEY FINDING: GPT-4o-mini under compliance pressure")
    print("=" * 60)

    mini = analysis["per_model_condition"].get("gpt-4o-mini", {})
    d = mini.get("D", {})
    g3 = mini.get("G3", {})

    if d.get("soundness_rate") is not None and g3.get("soundness_rate") is not None:
        d_rate = d["soundness_rate"]
        g3_rate = g3["soundness_rate"]
        d_n = d["executable_properties"]
        g3_n = g3["executable_properties"]
        delta = (g3_rate - d_rate) * 100
        h = cohens_h(d_rate, g3_rate)
        z = two_proportion_z(d_rate, d_n, g3_rate, g3_n)
        p = p_value_from_z(z)

        print(f"  Baseline (D):   {d_rate*100:.1f}% soundness (n={d_n})")
        print(f"  Pressure (G3):  {g3_rate*100:.1f}% soundness (n={g3_n})")
        print(f"  Delta:          {delta:+.1f} pp")
        print(f"  Cohen's h:      {h:+.3f}")
        print(f"  z-statistic:    {z:+.3f}")
        print(f"  p-value:        {p:.4e}")
        print(f"  Significant (p<0.05): {'YES' if p < 0.05 else 'NO'}")
        print(f"  Significant (Bonferroni p<0.017): {'YES' if p < 0.017 else 'NO'}")


if __name__ == "__main__":
    main()
