import json
import os
import re
import unittest
from redact import redact

# Fake key: "rly_" followed by 24 letters/digits
BODY = "Ab3dE6gH9jK2mN5pQ8sT1vX4"

# Line breaks tested. The packet does not say which kind the real comment used
# (see deliverables/unverified.md), so we cover the two most common.
NEWLINES = {
    "LF \\n": "\n",
    "CRLF \\r\\n": "\r\n",
}


class TestRedact(unittest.TestCase):
    def assert_no_leak(self, text):
        """Fail if any 4-character piece of the key body survives redaction."""
        out = redact(text)
        print(f"\n    before: {text!r}")
        print(f"    after:  {out!r}")
        for i in range(len(BODY) - 3):
            piece = BODY[i:i + 4]
            self.assertNotIn(piece, out, f"key leaked in output: {out!r}")

    def test_unbroken(self):
        self.assert_no_leak(f"key: rly_{BODY}")

    def test_hyphen_in_middle(self):
        self.assert_no_leak(f"key: rly_{BODY[:12]}-{BODY[12:]}")

    def test_newline_in_middle(self):
        for name, nl in NEWLINES.items():
            with self.subTest(newline=name):
                self.assert_no_leak(f"key: rly_{BODY[:12]}{nl}{BODY[12:]}")

    def test_bearer_unbroken(self):
        self.assert_no_leak(f"Authorization: Bearer rly_{BODY}")

    def test_bearer_hyphen_in_middle(self):
        self.assert_no_leak(f"Authorization: Bearer rly_{BODY[:16]}-{BODY[16:]}")

    def test_bearer_newline_in_middle(self):
        for name, nl in NEWLINES.items():
            with self.subTest(newline=name):
                self.assert_no_leak(f"Authorization: Bearer rly_{BODY[:20]}{nl}{BODY[20:]}")

    def test_bearer_newline_near_beginning(self):
        for name, nl in NEWLINES.items():
            with self.subTest(newline=name):
                self.assert_no_leak(f"Authorization: Bearer rly_{BODY[:3]}{nl}{BODY[3:]}")


# ---------------------------------------------------------------------------
# Your own inputs. Set REDACT_INPUTS to a JSON file (run_tests.py --inputs does
# this for you). Each case is an object:
#   "name":   a label (optional)
#   "text":   the text to run through redact()
#   "secret": the unbroken secret hidden in the text (optional)
# With a "secret", the test fails if any 4-character piece of it survives.
# Without one, the test checks that the text comes back unchanged.
# ---------------------------------------------------------------------------
def _pieces(secret):
    body = secret[4:] if secret.startswith("rly_") else secret
    if len(body) < 4:
        return [body]
    return [body[i:i + 4] for i in range(len(body) - 3)]


def _load_custom_cases():
    path = os.environ.get("REDACT_INPUTS")
    if not path:
        return []
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _make_test(case):
    def test(self):
        text = case["text"]
        secret = case.get("secret")
        out = redact(text)
        print(f"\n    before: {text!r}")
        print(f"    after:  {out!r}")
        if secret:
            for piece in _pieces(secret):
                self.assertNotIn(piece, out, f"secret leaked in output: {out!r}")
        else:
            self.assertEqual(out, text, "text without a secret should not change")
    return test


class TestCustomInputs(unittest.TestCase):
    """One test per case in the REDACT_INPUTS file (none if it is not set)."""


for _number, _case in enumerate(_load_custom_cases(), start=1):
    _label = re.sub(r"\W+", "_", str(_case.get("name", ""))).strip("_")
    setattr(TestCustomInputs, f"test_custom_{_number:03d}_{_label}", _make_test(_case))


if __name__ == "__main__":
    unittest.main(verbosity=2)
