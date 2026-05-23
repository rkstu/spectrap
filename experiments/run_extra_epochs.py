"""Extra epochs to push significance + Claude immunity test."""
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


FUNCTIONS = list(FUNCTION_CONTEXT.keys())
OUTPUT_DIR = Path(__file__).parent.parent / "generated" / "extra"


def run_extra_gpt4o_mini():
    """3 more epochs of GPT-4o-mini on D and G3 to push significance."""
    results = []
    conditions = ["D", "G3"]
    model = "gpt-4o-mini"

    total = len(FUNCTIONS) * len(conditions) * 3
    done = 0

    print("=" * 60)
    print("Extra epochs: GPT-4o-mini D+G3 (epochs 3-5)")
    print(f"  Total: {total} generations")
    print("=" * 60)

    for func in FUNCTIONS:
        for cond in conditions:
            for epoch in range(3, 6):  # epochs 3,4,5
                done += 1
                print(f"  [{done}/{total}] {func} | {cond} | {model} | e{epoch}", end=" ... ")
                sys.stdout.flush()
                try:
                    gen = generate_spec(func, cond, model, OUTPUT_DIR / "gpt4o_mini_extra", epoch)
                    val = validate_file(Path(gen["output_path"]))
                    gen["validation"] = val.to_dict()
                    gen.pop("raw_response", None)
                    results.append(gen)
                    print(f"{val.classification}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append({"function": func, "condition": cond, "model": model,
                                    "epoch": epoch, "error": str(e)})
                time.sleep(0.5)

    return results


def run_claude():
    """Run Claude Sonnet on all conditions to show immunity."""
    results = []
    conditions = ["D", "G3", "G4", "F"]
    model = "claude-sonnet-4-20250514"

    # Use Anthropic via OpenAI-compatible endpoint? No — use OpenRouter
    # Actually let's use the Anthropic API via openai-compatible wrapper
    # OpenRouter is simplest
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

    total = len(FUNCTIONS) * len(conditions) * 2  # 2 epochs for claude
    done = 0

    print("\n" + "=" * 60)
    print("Claude Sonnet run (via OpenRouter)")
    print(f"  Total: {total} generations")
    print("=" * 60)

    from spectrap.generate import generate_spec as gen_spec
    import importlib
    import spectrap.generate
    # Patch the client to use OpenRouter
    orig_key = os.environ.get("OPENROUTER_API_KEY", "")

    for func in FUNCTIONS:
        for cond in conditions:
            for epoch in range(2):
                done += 1
                print(f"  [{done}/{total}] {func} | {cond} | claude-sonnet | e{epoch}", end=" ... ")
                sys.stdout.flush()
                try:
                    gen = generate_spec(func, cond, "anthropic/claude-sonnet-4-20250514",
                                       OUTPUT_DIR / "claude", epoch)
                    val = validate_file(Path(gen["output_path"]))
                    gen["validation"] = val.to_dict()
                    gen.pop("raw_response", None)
                    results.append(gen)
                    print(f"{val.classification}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append({"function": func, "condition": cond, "model": "claude-sonnet",
                                    "epoch": epoch, "error": str(e)})
                time.sleep(1)

    return results


def main():
    all_extra = []

    # Run GPT-4o-mini extra epochs (using original OpenAI key)
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
    gpt_results = run_extra_gpt4o_mini()
    all_extra.extend(gpt_results)

    # Run Claude (switch to OpenRouter)
    claude_results = run_claude()
    all_extra.extend(claude_results)

    # Save
    results_path = Path(__file__).parent.parent / "results" / "extra_results.json"
    results_path.write_text(json.dumps(all_extra, indent=2))
    print(f"\n  Extra results saved: {results_path}")

    # Quick summary
    print("\n  GPT-4o-mini extra summary:")
    for cond in ["D", "G3"]:
        entries = [r for r in gpt_results if r.get("condition") == cond and "validation" in r and "num_passed" in r.get("validation", {})]
        passed = sum(e["validation"]["num_passed"] for e in entries)
        failed = sum(e["validation"]["num_failed"] for e in entries)
        total = passed + failed
        rate = f"{100*passed/total:.1f}%" if total > 0 else "N/A"
        print(f"    {cond}: {passed}/{total} sound ({rate})")

    print("\n  Claude summary:")
    for cond in ["D", "G3", "G4", "F"]:
        entries = [r for r in claude_results if r.get("condition") == cond and "validation" in r and "num_passed" in r.get("validation", {})]
        passed = sum(e["validation"]["num_passed"] for e in entries)
        failed = sum(e["validation"]["num_failed"] for e in entries)
        total = passed + failed
        rate = f"{100*passed/total:.1f}%" if total > 0 else "N/A"
        print(f"    {cond}: {passed}/{total} sound ({rate})")


if __name__ == "__main__":
    main()
