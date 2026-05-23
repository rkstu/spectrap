"""Run Claude Sonnet via OpenRouter."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

from spectrap.generate import generate_spec
from spectrap.validate import validate_file
from spectrap.prompts import FUNCTION_CONTEXT

FUNCTIONS = list(FUNCTION_CONTEXT.keys())
CONDITIONS = ["D", "G3", "G4", "F"]
MODEL = "anthropic/claude-sonnet-4"
EPOCHS = 2
OUTPUT_DIR = Path(__file__).parent.parent / "generated" / "claude"


def main():
    total = len(FUNCTIONS) * len(CONDITIONS) * EPOCHS
    print(f"Claude Sonnet run: {total} generations")

    results = []
    done = 0

    for func in FUNCTIONS:
        for cond in CONDITIONS:
            for epoch in range(EPOCHS):
                done += 1
                print(f"  [{done}/{total}] {func} | {cond} | claude-sonnet | e{epoch}", end=" ... ")
                sys.stdout.flush()
                try:
                    gen = generate_spec(func, cond, MODEL, OUTPUT_DIR, epoch)
                    val = validate_file(Path(gen["output_path"]))
                    gen["validation"] = val.to_dict()
                    gen.pop("raw_response", None)
                    # Normalize model name for analysis
                    gen["model"] = "claude-sonnet-4"
                    results.append(gen)
                    print(f"{val.classification} ({val.num_passed}P/{val.num_failed}F/{val.num_errored}E)")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append({"function": func, "condition": cond, "model": "claude-sonnet-4",
                                    "epoch": epoch, "error": str(e)})
                time.sleep(1.5)

    # Save
    results_path = Path(__file__).parent.parent / "results" / "claude_results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {results_path}")

    # Quick summary
    for cond in CONDITIONS:
        entries = [r for r in results if r.get("condition") == cond and "validation" in r and "num_passed" in r.get("validation", {})]
        passed = sum(e["validation"]["num_passed"] for e in entries)
        failed = sum(e["validation"]["num_failed"] for e in entries)
        total_exec = passed + failed
        rate = f"{100*passed/total_exec:.1f}%" if total_exec > 0 else "N/A"
        print(f"  {cond}: {passed}/{total_exec} sound ({rate})")


if __name__ == "__main__":
    main()
