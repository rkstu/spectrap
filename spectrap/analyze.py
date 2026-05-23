"""Statistical analysis for SpecTrap experiment results."""
import json
import math
from collections import defaultdict
from pathlib import Path


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for proportions (arcsine transformation)."""
    return 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))


def two_proportion_z(p1: float, n1: int, p2: float, n2: int) -> float:
    """Two-proportion z-test statistic."""
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    if p_pool == 0 or p_pool == 1:
        return 0.0
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    if se == 0:
        return 0.0
    return (p1 - p2) / se


def p_value_from_z(z: float) -> float:
    """Approximate two-tailed p-value from z-score using normal CDF."""
    # Abramowitz and Stegun approximation
    x = abs(z)
    t = 1 / (1 + 0.2316419 * x)
    d = 0.3989422804 * math.exp(-x * x / 2)
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    return 2 * p


def analyze_results(results_path: Path) -> dict:
    """Analyze experiment results and compute statistics."""
    data = json.loads(results_path.read_text())

    # Group by model × condition
    groups = defaultdict(lambda: {"props": 0, "passed": 0, "failed": 0, "errored": 0,
                                   "files": 0, "sound_files": 0, "unsound_files": 0,
                                   "hallucinated_api": 0})

    for entry in data:
        model = entry.get("model", "unknown")
        cond = entry.get("condition", "unknown")
        val = entry.get("validation", {})
        key = (model, cond)

        if "num_properties" not in val:
            continue

        groups[key]["files"] += 1
        groups[key]["props"] += val["num_properties"]
        groups[key]["passed"] += val["num_passed"]
        groups[key]["failed"] += val["num_failed"]
        groups[key]["errored"] += val["num_errored"]

        cls = val.get("classification", "")
        if cls == "sound":
            groups[key]["sound_files"] += 1
        elif cls == "unsound":
            groups[key]["unsound_files"] += 1

        # Count API hallucinations (errored at import time)
        for f in val.get("failures", []):
            if f.get("error_type") == "CollectionError":
                groups[key]["hallucinated_api"] += 1

    # Compute metrics
    analysis = {}
    models = sorted(set(k[0] for k in groups))
    conditions = sorted(set(k[1] for k in groups))

    for model in models:
        analysis[model] = {}
        for cond in conditions:
            g = groups.get((model, cond), groups[("", "")])
            executable = g["passed"] + g["failed"]
            fail_rate = g["failed"] / executable if executable > 0 else None
            soundness = g["passed"] / executable if executable > 0 else None
            err_rate = g["errored"] / g["props"] if g["props"] > 0 else None

            analysis[model][cond] = {
                "files": g["files"],
                "total_properties": g["props"],
                "passed": g["passed"],
                "failed": g["failed"],
                "errored": g["errored"],
                "executable_properties": executable,
                "fail_rate": fail_rate,
                "soundness_rate": soundness,
                "error_rate": err_rate,
                "file_soundness": g["sound_files"] / g["files"] if g["files"] > 0 else None,
                "hallucinated_api_count": g["hallucinated_api"],
            }

    # Compute comparisons (each condition vs baseline D)
    comparisons = {}
    for model in models:
        comparisons[model] = {}
        baseline = analysis[model].get("D", {})
        base_soundness = baseline.get("soundness_rate")
        base_n = baseline.get("executable_properties", 0)

        for cond in conditions:
            if cond == "D":
                continue
            target = analysis[model].get(cond, {})
            target_soundness = target.get("soundness_rate")
            target_n = target.get("executable_properties", 0)

            if base_soundness is not None and target_soundness is not None and base_n > 0 and target_n > 0:
                h = cohens_h(base_soundness, target_soundness)
                z = two_proportion_z(base_soundness, base_n, target_soundness, target_n)
                p = p_value_from_z(z)
                delta = target_soundness - base_soundness
                comparisons[model][cond] = {
                    "baseline_soundness": base_soundness,
                    "target_soundness": target_soundness,
                    "delta_pp": delta * 100,
                    "cohens_h": h,
                    "z_statistic": z,
                    "p_value": p,
                    "significant_005": p < 0.05,
                    "significant_bonferroni": p < (0.05 / (len(conditions) - 1)),
                }

    return {
        "per_model_condition": analysis,
        "comparisons_vs_baseline": comparisons,
        "models": models,
        "conditions": conditions,
    }


def print_report(analysis: dict):
    """Print a formatted report."""
    models = analysis["models"]
    conditions = analysis["conditions"]

    print("\n" + "=" * 80)
    print("SpecTrap Experiment Results — Property-Level Soundness Analysis")
    print("=" * 80)

    # Table 1: Soundness rates
    print(f"\n{'Model':<16} {'Cond':<6} {'n(exec)':<9} {'Soundness':<11} {'FailRate':<10} {'ErrRate':<10} {'HalAPI':<7}")
    print("-" * 75)
    for model in models:
        for cond in conditions:
            d = analysis["per_model_condition"][model].get(cond, {})
            n = d.get("executable_properties", 0)
            snd = f"{d['soundness_rate']*100:.1f}%" if d.get("soundness_rate") is not None else "N/A"
            fr = f"{d['fail_rate']*100:.1f}%" if d.get("fail_rate") is not None else "N/A"
            er = f"{d['error_rate']*100:.1f}%" if d.get("error_rate") is not None else "N/A"
            hal = d.get("hallucinated_api_count", 0)
            print(f"{model:<16} {cond:<6} {n:<9} {snd:<11} {fr:<10} {er:<10} {hal:<7}")
        print()

    # Table 2: Statistical comparisons
    print("\nStatistical Comparisons (each condition vs Baseline D):")
    print("-" * 80)
    print(f"{'Model':<16} {'Cond':<6} {'Δpp':<8} {'Cohen h':<9} {'z':<8} {'p':<12} {'Sig?':<6}")
    print("-" * 80)
    for model in models:
        comps = analysis["comparisons_vs_baseline"].get(model, {})
        for cond, stats in comps.items():
            sig = "***" if stats["significant_bonferroni"] else ("*" if stats["significant_005"] else "")
            print(
                f"{model:<16} {cond:<6} "
                f"{stats['delta_pp']:>+6.1f}  "
                f"{stats['cohens_h']:>+7.3f}  "
                f"{stats['z_statistic']:>+6.2f}  "
                f"{stats['p_value']:<12.2e} "
                f"{sig:<6}"
            )
        print()


if __name__ == "__main__":
    results_path = Path(__file__).parent.parent / "results" / "experiment_results.json"
    if results_path.exists():
        analysis = analyze_results(results_path)
        print_report(analysis)
        # Save analysis
        out = Path(__file__).parent.parent / "results" / "analysis.json"
        out.write_text(json.dumps(analysis, indent=2, default=str))
        print(f"\n  Analysis saved: {out}")
    else:
        print(f"No results found at {results_path}")
