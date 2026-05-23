"""Validate generated specs: run them with Hypothesis and classify failures."""
import ast
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ValidationResult:
    file_path: str
    syntactically_valid: bool
    num_properties: int
    num_passed: int
    num_failed: int
    num_errored: int
    failures: list  # list of {test_name, error_type, error_message}
    classification: str  # "sound", "unsound", "errored", "vacuous", "unparseable"

    def to_dict(self):
        return asdict(self)


def count_test_functions(code: str) -> int:
    """Count functions decorated with @given or named test_*."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            count += 1
    return count


def check_vacuity(code: str) -> bool:
    """Quick heuristic: does the test body contain only 'assert True' or pass?"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            body_src = ast.dump(node)
            if "assert True" in ast.unparse(node) and "==" not in ast.unparse(node):
                return True
    return False


def validate_file(file_path: Path, timeout: int = 60) -> ValidationResult:
    """Run a generated test file and classify the result."""
    code = file_path.read_text()

    # 1. Syntactic validity
    try:
        ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(
            file_path=str(file_path),
            syntactically_valid=False,
            num_properties=0,
            num_passed=0,
            num_failed=0,
            num_errored=0,
            failures=[{"test_name": "parse", "error_type": "SyntaxError", "error_message": str(e)}],
            classification="unparseable",
        )

    num_props = count_test_functions(code)

    if num_props == 0:
        return ValidationResult(
            file_path=str(file_path),
            syntactically_valid=True,
            num_properties=0,
            num_passed=0,
            num_failed=0,
            num_errored=0,
            failures=[],
            classification="vacuous",
        )

    # 2. Vacuity check
    if check_vacuity(code):
        return ValidationResult(
            file_path=str(file_path),
            syntactically_valid=True,
            num_properties=num_props,
            num_passed=num_props,
            num_failed=0,
            num_errored=0,
            failures=[],
            classification="vacuous",
        )

    # 3. Run with pytest + hypothesis
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(file_path), "-v", "--tb=short",
         "--hypothesis-seed=0", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(file_path.parent),
    )

    # Parse pytest output
    passed, failed, errored = 0, 0, 0
    failures = []

    for line in result.stdout.split("\n"):
        if " PASSED" in line:
            passed += 1
        elif " FAILED" in line:
            failed += 1
            test_name = line.split("::")[1].split(" ")[0] if "::" in line else "unknown"
            failures.append({
                "test_name": test_name,
                "error_type": "AssertionError",
                "error_message": "",
            })
        elif " ERROR" in line:
            errored += 1

    # Also check stderr for import errors etc
    if result.returncode != 0 and failed == 0 and passed == 0:
        errored = num_props
        error_msg = result.stderr[:500] if result.stderr else result.stdout[:500]
        failures.append({
            "test_name": "import/collection",
            "error_type": "CollectionError",
            "error_message": error_msg,
        })

    # Classify
    if errored > 0 and passed == 0 and failed == 0:
        classification = "errored"
    elif failed > 0:
        classification = "unsound"
    else:
        classification = "sound"

    return ValidationResult(
        file_path=str(file_path),
        syntactically_valid=True,
        num_properties=num_props,
        num_passed=passed,
        num_failed=failed,
        num_errored=errored,
        failures=failures,
        classification=classification,
    )


def validate_batch(directory: Path, timeout: int = 60) -> list[ValidationResult]:
    """Validate all generated test files in a directory."""
    results = []
    for f in sorted(directory.glob("*.py")):
        if f.name.endswith(".meta.json"):
            continue
        print(f"  Validating: {f.name}")
        r = validate_file(f, timeout)
        print(f"    → {r.classification} ({r.num_passed}P/{r.num_failed}F/{r.num_errored}E)")
        results.append(r)
    return results
