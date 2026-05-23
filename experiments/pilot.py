"""Pilot run: 1 function × 2 conditions × 1 model → end-to-end validation."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spectrap.generate import run_pilot
from spectrap.validate import validate_batch


def main():
    output_dir = Path(__file__).parent.parent / "generated" / "pilot"

    print("=" * 60)
    print("SpecTrap Pilot Run")
    print("  Function: json_roundtrip")
    print("  Conditions: D (baseline), G3 (compliance pressure)")
    print("  Model: gpt-4o-mini")
    print("  Epochs: 1")
    print("=" * 60)

    # Step 1: Generate
    print("\n[1/3] Generating specs under pressure conditions...")
    gen_results = run_pilot(
        function_key="json_roundtrip",
        conditions=["D", "G3"],
        model="gpt-4o-mini",
        output_dir=output_dir,
        epochs=1,
    )

    print(f"\n  Generated {len(gen_results)} spec files.")

    # Step 2: Validate
    print("\n[2/3] Validating generated specs...")
    val_results = validate_batch(output_dir)

    # Step 3: Report
    print("\n[3/3] Results:")
    print("-" * 60)
    print(f"{'Condition':<12} {'Classification':<14} {'Props':<6} {'Pass':<5} {'Fail':<5} {'Err':<5}")
    print("-" * 60)

    for gen, val in zip(gen_results, val_results):
        print(
            f"{gen['condition']:<12} "
            f"{val.classification:<14} "
            f"{val.num_properties:<6} "
            f"{val.num_passed:<5} "
            f"{val.num_failed:<5} "
            f"{val.num_errored:<5}"
        )

    print("-" * 60)

    # Summary
    d_result = next((v for g, v in zip(gen_results, val_results) if g["condition"] == "D"), None)
    g3_result = next((v for g, v in zip(gen_results, val_results) if g["condition"] == "G3"), None)

    if d_result and g3_result:
        d_sound = d_result.classification == "sound"
        g3_sound = g3_result.classification == "sound"
        print(f"\n  Baseline (D): {'SOUND' if d_sound else 'UNSOUND/ERROR'}")
        print(f"  Pressure (G3): {'SOUND' if g3_sound else 'UNSOUND/ERROR'}")
        if d_sound and not g3_sound:
            print("\n  ✓ SIGNAL DETECTED: Compliance pressure degrades spec soundness!")
        elif not d_sound:
            print("\n  ⚠ Baseline also unsound — may need to tune prompts or check validation")
        else:
            print("\n  – No signal in this single sample. Need more epochs for statistics.")

    # Save results
    results_path = Path(__file__).parent.parent / "results" / "pilot_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    combined = []
    for gen, val in zip(gen_results, val_results):
        combined.append({**gen, "validation": val.to_dict()})
    # Remove raw_response for cleaner output
    for r in combined:
        r.pop("raw_response", None)
    results_path.write_text(json.dumps(combined, indent=2))
    print(f"\n  Results saved to: {results_path}")


if __name__ == "__main__":
    main()
