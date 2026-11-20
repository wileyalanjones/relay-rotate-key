import unittest
from redact import redact

# Fake key: "rly_" followed by 24 letters/digits
BODY = "Ab3dE6gH9jK2mN5pQ8sT1vX4"

# Different kinds of line breaks a chat tool or OS might use
NEWLINES = {
    "LF \\n": "\n",
    "CRLF \\r\\n": "\r\n",
    "CR \\r": "\r",
    "vertical tab \\v": "\v",
    "form feed \\f": "\f",
    "NEL \\x85": "\x85",
    "line separator \\u2028": " ",
    "paragraph separator \\u2029": " ",
}


class TestRedact(unittest.TestCase):
    def assert_no_leak(self, text):
        """Fail if any 4-character piece of the key body survives redaction."""
        out = redact(text)
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


if __name__ == "__main__":
    unittest.main()
