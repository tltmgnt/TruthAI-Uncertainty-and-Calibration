"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")

def sample(path):
    return json.loads((ROOT / path).read_text())



def run():
    from uncertainty_calibration.metrics import evaluate
    data = sample("examples/binary.json")
    r = evaluate(data)
    check("hand-computed Brier score", round(r["brier_score"],12), .225)
    check("descriptive accuracy", r["accuracy"], .5)
    check("selective coverage", r["abstention"]["coverage"], .5)
    check("selective accuracy", r["abstention"]["selective_accuracy"], 1.0)
    bad = copy.deepcopy(data); bad["evaluation"] = [{"id":"impossible","probability":0,"outcome":1}]
    q = evaluate(bad)
    check("impossible observation has infinite log loss", q["log_loss_status"], "positive_infinity")
    check("infinity is explicit null, not clipped", q["log_loss"], None)
    bad["evaluation"][0]["probability"] = .5
    q = evaluate(bad)
    check("empty abstention leaves accuracy undefined", q["abstention"]["selective_accuracy"], None)
    check("no population calibration established", r["population_calibration_established"], False)
    bad = copy.deepcopy(data); bad["evaluation"][0]["probability"] = True
    rejects("boolean probability rejected", lambda: evaluate(bad))

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
