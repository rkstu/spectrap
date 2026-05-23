"""Main experiment: 5 functions × 4 conditions × N models × 3 epochs."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from spectrap.generate import generate_spec
from spectrap.validate import validate_file


FUNCTIONS = ["json_roundtrip", "base64_roundtrip", "sorted_invariants", "urllib_quote_roundtrip", "set_operations"]
CONDITIONS = ["D", "G3", "G4", "F"]
MODELS = ["gpt-4o-mini", "gpt-4o"]
EPOCHS = 3


def main():
    output_dir = Path(__file__).parent.parent / "generated" / "main"
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    total = len(FUNCTIONS) * len(CONDITIONS) * len(MODELS) * EPOCHS
    print("=" * 70)
    print("SpecTrap Main Experiment")
    print(f"  Functions: {len(FUNCTIONS)}")
    print(f"  Conditions: {CONDITIONS}")
    print(f"  Models: {MODELS}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Total generations: {total}")
    print("=" * 70)

    all_results = []
    done = 0

    for func in FUNCTIONS:
        for cond in CONDITIONS:
            for model in MODELS:
                for epoch in range(EPOCHS):
                    done += 1
                    tag = f"[{done}/{total}]"
                    print(f"  {tag} {func} | {cond} | {model} | e{epoch}", end=" ... ")
                    sys.stdout.flush()

                    try:
                        gen = generate_spec(func, cond, model, output_dir, epoch)
                        val = validate_file(Path(gen["output_path"]))
                        gen["validation"] = val.to_dict()
                        gen.pop("raw_response", None)
                        all_results.append(gen)
                        print(f"{val.classification} ({val.num_passed}P/{val.num_failed}F/{val.num_errored}E)")
                    except Exception as e:
                        print(f"ERROR: {e}")
                        all_results.append({
                            "function": func, "condition": cond, "model": model,
                            "epoch": epoch, "error": str(e),
                            "validation": {"classification": "generation_error"}
                        })

                    time.sleep(0.5)

    # Save raw results
    raw_path = results_dir / "experiment_results.json"
    raw_path.write_text(json.dumps(all_results, indent=2))
    print(f"\n  Raw results: {raw_path}")

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY: Property-Level Failure Rate by Condition × Model")
    print("=" * 70)
    print(f"{'Model':<16} {'Cond':<6} {'Files':<6} {'Props':<6} {'Pass':<6} {'Fail':<6} {'Err':<6} {'FailRate':<10} {'ErrRate':<10}")
    print("-" * 75)

    for model in MODELS:
        for cond in CONDITIONS:
            entries = [r for r in all_results if r.get("model") == model and r.get("condition") == cond and "validation" in r and "num_properties" in r.get("validation", {})]
            files = len(entries)
            props = sum(e["validation"]["num_properties"] for e in entries)
            passed = sum(e["validation"]["num_passed"] for e in entries)
            failed = sum(e["validation"]["num_failed"] for e in entries)
            errored = sum(e["validation"]["num_errored"] for e in entries)
            executable = passed + failed
            fail_rate = f"{100*failed/executable:.1f}%" if executable > 0 else "N/A"
            err_rate = f"{100*errored/props:.1f}%" if props > 0 else "N/A"
            print(f"{model:<16} {cond:<6} {files:<6} {props:<6} {passed:<6} {failed:<6} {errored:<6} {fail_rate:<10} {err_rate:<10}")
        print()


if __name__ == "__main__":
    main()
