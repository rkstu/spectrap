"""SpecTrap CLI — pip-installable adversarial robustness testing for AI spec generators."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from .generate import generate_spec
from .validate import validate_file, validate_batch
from .prompts import FUNCTION_CONTEXT, CONDITIONS
from .analyze import analyze_results, print_report


def cmd_run(args):
    """Run SpecTrap evaluation."""
    functions = args.functions.split(",") if args.functions != "all" else list(FUNCTION_CONTEXT.keys())
    conditions = args.conditions.split(",") if args.conditions != "all" else list(CONDITIONS.keys())
    models = args.models.split(",")
    epochs = args.epochs
    output_dir = Path(args.output)

    total = len(functions) * len(conditions) * len(models) * epochs
    print(f"SpecTrap: {total} spec generations ({len(functions)} funcs × {len(conditions)} conds × {len(models)} models × {epochs} epochs)")

    results = []
    done = 0

    for func in functions:
        for cond in conditions:
            for model in models:
                for epoch in range(epochs):
                    done += 1
                    print(f"  [{done}/{total}] {func} | {cond} | {model} | e{epoch}", end=" ... ")
                    sys.stdout.flush()
                    try:
                        gen = generate_spec(func, cond, model, output_dir, epoch)
                        val = validate_file(Path(gen["output_path"]))
                        gen["validation"] = val.to_dict()
                        gen.pop("raw_response", None)
                        results.append(gen)
                        print(f"{val.classification}")
                    except Exception as e:
                        print(f"ERROR: {e}")
                        results.append({"function": func, "condition": cond, "model": model,
                                        "epoch": epoch, "error": str(e)})
                    time.sleep(0.3)

    results_path = output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {results_path}")


def cmd_report(args):
    """Generate report from results."""
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Not found: {results_path}")
        sys.exit(1)

    analysis = analyze_results(results_path)
    print_report(analysis)

    if args.format == "json":
        out = results_path.parent / "analysis.json"
        out.write_text(json.dumps(analysis, indent=2, default=str))
        print(f"\nJSON analysis: {out}")


def cmd_validate(args):
    """Validate a single generated test file."""
    result = validate_file(Path(args.file))
    print(f"Classification: {result.classification}")
    print(f"Properties: {result.num_properties} (P:{result.num_passed} F:{result.num_failed} E:{result.num_errored})")
    if result.failures:
        for f in result.failures:
            print(f"  FAIL: {f['test_name']} — {f['error_type']}")


def main():
    parser = argparse.ArgumentParser(prog="spectrap", description="Adversarial robustness testing for AI spec generators")
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Run SpecTrap evaluation")
    p_run.add_argument("--functions", default="all", help="Comma-separated function keys or 'all'")
    p_run.add_argument("--conditions", default="all", help="Comma-separated condition keys or 'all'")
    p_run.add_argument("--models", default="gpt-4o-mini", help="Comma-separated model names")
    p_run.add_argument("--epochs", type=int, default=3, help="Epochs per condition")
    p_run.add_argument("--output", default="generated/spectrap_run", help="Output directory")

    # report
    p_report = sub.add_parser("report", help="Generate report from results")
    p_report.add_argument("--results", default="generated/spectrap_run/results.json", help="Path to results JSON")
    p_report.add_argument("--format", choices=["markdown", "json"], default="markdown")

    # validate
    p_val = sub.add_parser("validate", help="Validate a single generated test file")
    p_val.add_argument("file", help="Path to generated test file")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
