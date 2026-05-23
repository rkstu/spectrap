"""Generate final report after experiment completes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spectrap.analyze import analyze_results, print_report
from spectrap.visualize import ascii_cliff_plot, markdown_report


def main():
    results_path = Path(__file__).parent.parent / "results" / "experiment_results.json"
    if not results_path.exists():
        print(f"No results at {results_path}")
        return

    analysis = analyze_results(results_path)

    # Console output
    print_report(analysis)
    print("\n")
    print(ascii_cliff_plot(analysis))

    # Markdown report
    report = markdown_report(analysis)
    report_path = results_path.parent / "REPORT.md"
    report_path.write_text(report)
    print(f"\nMarkdown report saved: {report_path}")

    # JSON analysis
    import json
    analysis_path = results_path.parent / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, indent=2, default=str))
    print(f"JSON analysis saved: {analysis_path}")


if __name__ == "__main__":
    main()
