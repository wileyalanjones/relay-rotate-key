"""Run the same unit tests against the original and the fixed redact module.

Usage (from the helpers/ folder):
    python3 run_tests.py                          the built-in tests
    python3 run_tests.py --inputs my_inputs.json  the built-in tests plus your own

The tests in test_redact_unit.py import `redact` from either redact.py or
redact_fixed.py. For each module below we register it under both names and
re-import the tests, so the test file itself never has to change.
"""
import argparse
import importlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

parser = argparse.ArgumentParser(description="Run the redact tests on both modules.")
parser.add_argument(
    "--inputs",
    metavar="FILE.json",
    help="also run your own inputs: a JSON list of "
    '{"name": "...", "text": "...", "secret": "..."} (see example_inputs.json)',
)
args = parser.parse_args()

if args.inputs:
    path = os.path.abspath(args.inputs)
    try:
        with open(path, encoding="utf-8") as handle:
            cases = json.load(handle)
        assert isinstance(cases, list)
        for case in cases:
            assert isinstance(case, dict) and isinstance(case.get("text"), str)
    except (OSError, ValueError, AssertionError) as error:
        sys.exit(
            f"Could not use {args.inputs}: it must be a JSON list of objects, "
            f'each with a "text" string ({str(error) or "wrong shape"}).'
        )
    os.environ["REDACT_INPUTS"] = path
    print(f"Also running {len(cases)} custom input(s) from {args.inputs}\n")

MODULES = ["redact", "redact_fixed"]  # original first, then the fix
LOADED = {name: importlib.import_module(name) for name in MODULES}  # import before any swapping
results = {}

for name in MODULES:
    print("=" * 70)
    print(f"RUNNING TESTS AGAINST: {name}.py")
    print("=" * 70)

    module = LOADED[name]
    # Register under both names so the tests use the module under test no
    # matter which of the two imports test_redact_unit.py currently has.
    sys.modules["redact"] = module
    sys.modules["redact_fixed"] = module
    sys.modules.pop("test_redact_unit", None)  # force a fresh import
    tests = unittest.defaultTestLoader.loadTestsFromName("test_redact_unit")

    result = unittest.TextTestRunner(verbosity=2).run(tests)
    results[name] = result
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
for name, r in results.items():
    problems = len(r.failures) + len(r.errors)
    status = "PASS" if r.wasSuccessful() else "FAIL"
    print(f"{name + '.py':<18} {status}  ran={r.testsRun}  failing checks={problems}")

# Expected: the original fails, the fix passes.
sys.exit(0 if results["redact_fixed"].wasSuccessful() else 1)
