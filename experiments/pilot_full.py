"""Full pilot: 1 function × 4 conditions × 1 model × 3 epochs."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

from spectrap.generate import run_pilot
from spectrap.validate import validate_batch


def main():
    output_dir = Path(__file__).parent.parent / "generated" / "pilot_full"

    conditions = ["D", "G3", "G4", "F"]
    model = "gpt-4o-mini"
    epochs = 3

    print("=" * 60)
    print("SpecTrap Full Pilot")
    print(f"  Function: json_roundtrip")
    print(f"  Conditions: {conditions}")
    print(f"  Model: {model}")
    print(f"  Epochs: {epochs}")
    print(f"  Total generations: {len(conditions) * epochs}")
    print("=" * 60)

    # Generate
    print("\n[1/3] Generating specs...")
    gen_results = run_pilot(
        function_key="json_roundtrip",
        conditions=conditions,
        model=model,
        output_dir=output_dir,
        epochs=epochs,
    )
    print(f"\n  Generated {len(gen_results)} spec files.")

    # Validate
    print("\n[2/3] Validating...")
    val_results = validate_batch(output_dir)

    # Match gen to val by filename
    val_by_file = {Path(v.file_path).name: v for v in val_results}

    # Analyze per-condition
    print("\n[3/3] Per-Condition Analysis:")
    print("=" * 70)
    print(f"{'Condition':<8} {'Epoch':<6} {'Class':<12} {'Props':<6} {'Pass':<5} {'Fail':<5} {'Err':<5}")
    print("-" * 70)

    condition_stats = {}
    for gen in gen_results:
        fname = Path(gen["output_path"]).name
        val = val_by_file.get(fname)
        if not val:
            continue
        cond = gen["condition"]
        print(
            f"{cond:<8} {gen['epoch']:<6} "
            f"{val.classification:<12} "
            f"{val.num_properties:<6} "
            f"{val.num_passed:<5} "
            f"{val.num_failed:<5} "
            f"{val.num_errored:<5}"
        )

        if cond not in condition_stats:
            condition_stats[cond] = {"total": 0, "sound": 0, "unsound": 0, "errored": 0, "props": 0, "failed_props": 0}
        condition_stats[cond]["total"] += 1
        condition_stats[cond]["props"] += val.num_properties
        condition_stats[cond]["failed_props"] += val.num_failed
        if val.classification == "sound":
            condition_stats[cond]["sound"] += 1
        elif val.classification == "unsound":
            condition_stats[cond]["unsound"] += 1
        else:
            condition_stats[cond]["errored"] += 1

    print("\n" + "=" * 70)
    print("SUMMARY (per condition across epochs):")
    print(f"{'Cond':<6} {'Total':<6} {'Sound':<7} {'Unsound':<9} {'Error':<7} {'Soundness%':<12} {'Props':<6} {'FailProps':<10}")
    print("-" * 70)
    for cond in conditions:
        s = condition_stats.get(cond, {})
        total = s.get("total", 0)
        sound = s.get("sound", 0)
        pct = f"{100*sound/total:.1f}%" if total > 0 else "N/A"
        print(
            f"{cond:<6} {total:<6} {sound:<7} {s.get('unsound',0):<9} "
            f"{s.get('errored',0):<7} {pct:<12} "
            f"{s.get('props',0):<6} {s.get('failed_props',0):<10}"
        )

    # Save
    results_path = Path(__file__).parent.parent / "results" / "pilot_full_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    combined = []
    for gen in gen_results:
        fname = Path(gen["output_path"]).name
        val = val_by_file.get(fname)
        entry = {**gen, "validation": val.to_dict() if val else None}
        entry.pop("raw_response", None)
        combined.append(entry)
    results_path.write_text(json.dumps(combined, indent=2))
    print(f"\n  Full results: {results_path}")


if __name__ == "__main__":
    main()
