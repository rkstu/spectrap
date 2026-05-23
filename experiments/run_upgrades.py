"""Run all upgrade experiments: escape hatch + crypto targets + more GPT-4o epochs."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from spectrap.generate import generate_spec
from spectrap.validate import validate_file
from spectrap.prompts import FUNCTION_CONTEXT

STDLIB_FUNCS = ["json_roundtrip", "base64_roundtrip", "sorted_invariants", "urllib_quote_roundtrip", "set_operations"]
CRYPTO_FUNCS = ["crypto_fernet", "hashlib_sha256"]
ALL_FUNCS = STDLIB_FUNCS + CRYPTO_FUNCS


def run_batch(name, functions, conditions, models, epochs, output_subdir):
    """Run a batch of generations."""
    output_dir = Path(__file__).parent.parent / "generated" / output_subdir
    total = len(functions) * len(conditions) * len(models) * epochs
    done = 0
    results = []

    print(f"\n{'='*60}")
    print(f"BATCH: {name} ({total} generations)")
    print(f"{'='*60}")

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
                        print(f"{val.classification} ({val.num_passed}P/{val.num_failed}F/{val.num_errored}E)")
                    except Exception as e:
                        print(f"ERROR: {e}")
                        results.append({"function": func, "condition": cond, "model": model,
                                        "epoch": epoch, "error": str(e)})
                    time.sleep(0.5)

    return results


def summarize_file_level(results, conditions):
    """Print file-level soundness per condition."""
    print(f"\n  File-level soundness:")
    for cond in conditions:
        entries = [r for r in results if r.get("condition") == cond and "validation" in r and "classification" in r.get("validation", {})]
        sound = sum(1 for e in entries if e["validation"]["classification"] == "sound")
        n = len(entries)
        print(f"    {cond}: {sound}/{n} ({100*sound/n:.0f}%)" if n > 0 else f"    {cond}: N/A")


def main():
    all_results = []

    # BATCH 1: Escape hatch remediation (G3E vs G3 on GPT-4o-mini)
    # This is the MOST important — shows the fix works
    batch1 = run_batch(
        "Escape Hatch Remediation",
        functions=STDLIB_FUNCS,
        conditions=["G3", "G3E"],
        models=["gpt-4o-mini"],
        epochs=3,
        output_subdir="escape_hatch"
    )
    all_results.extend(batch1)
    summarize_file_level(batch1, ["G3", "G3E"])

    # BATCH 2: Crypto targets (real shipping code)
    batch2 = run_batch(
        "Crypto Targets (Real Shipping Code)",
        functions=CRYPTO_FUNCS,
        conditions=["D", "G3", "G4", "G3E"],
        models=["gpt-4o-mini", "gpt-4o"],
        epochs=2,
        output_subdir="crypto"
    )
    all_results.extend(batch2)
    summarize_file_level(batch2, ["D", "G3", "G4", "G3E"])

    # BATCH 3: More GPT-4o epochs on D and G4 (push significance)
    batch3 = run_batch(
        "GPT-4o Extra Epochs (D + G4)",
        functions=STDLIB_FUNCS,
        conditions=["D", "G4"],
        models=["gpt-4o"],
        epochs=3,  # epochs 3,4,5
        output_subdir="gpt4o_extra"
    )
    # Fix epoch numbering
    for r in batch3:
        if "epoch" in r:
            r["epoch"] += 3
    all_results.extend(batch3)
    summarize_file_level(batch3, ["D", "G4"])

    # Save all
    results_path = Path(__file__).parent.parent / "results" / "upgrade_results.json"
    results_path.write_text(json.dumps(all_results, indent=2))
    print(f"\n\nAll upgrade results saved: {results_path}")
    print(f"Total generations: {len(all_results)}")


if __name__ == "__main__":
    main()
