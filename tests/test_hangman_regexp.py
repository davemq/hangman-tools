"""Tests for hangman_regexp -x/--remove argument validation."""

import argparse
import contextlib
import io
import unittest
from unittest import mock

from hangman_tools import hangman_regexp


def run_main(*args):
    """Run main() with args; return (exit code or None, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = None
    with mock.patch("sys.argv", ["hangman-regexp", *args]), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            hangman_regexp.main()
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class SingleLetterTest(unittest.TestCase):
    def test_accepts_lowercase_letter(self):
        self.assertEqual(hangman_regexp.single_letter("a"), "a")

    def test_lowercases_uppercase_letter(self):
        self.assertEqual(hangman_regexp.single_letter("B"), "b")

    def test_rejects_invalid_values(self):
        for value in ["", "1", "ab", "-", "é", " "]:
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    hangman_regexp.single_letter(value)


class RemoveOptionTest(unittest.TestCase):
    def setUp(self):
        # main() accumulates into this module-level set; isolate each test.
        hangman_regexp.removed_chars.clear()

    def test_removes_given_letters(self):
        code, out, _ = run_main("-x", "a", "-x", "B", "h_ll_")
        self.assertIsNone(code)
        self.assertEqual(out.strip(), r"\<h[c-gi-km-z]ll[c-gi-km-z]\>")

    def test_repeated_letter_is_allowed(self):
        code, out, _ = run_main("-x", "a", "-x", "a", "h_ll_")
        self.assertIsNone(code)
        self.assertEqual(out.strip(), r"\<h[b-gi-km-z]ll[b-gi-km-z]\>")

    def test_invalid_values_give_usage_error(self):
        # Previously these raised IndexError from multi_split().
        for value in ["1", "ab", "ba", "é", ""]:
            with self.subTest(value=value):
                hangman_regexp.removed_chars.clear()
                code, out, err = run_main("-x", value, "h_ll_")
                self.assertEqual(code, 2)
                self.assertEqual(out, "")
                self.assertIn("must be a single letter a-z", err)


class PunctuationTest(unittest.TestCase):
    """Punctuation at the ends of a word must be outside \\< and \\>."""

    def setUp(self):
        hangman_regexp.removed_chars.clear()

    def check(self, phrase, expected, *opts):
        hangman_regexp.removed_chars.clear()
        code, out, _ = run_main(*opts, phrase)
        self.assertIsNone(code)
        self.assertEqual(out.strip(), expected)

    def test_trailing_comma_issue_49(self):
        self.check(
            "_ _ _ R _ / _ _ _ _ / _ _ / A / _ _ _ _ _ , /",
            r"\<[b-qsu-z]\{3\}r[b-qsu-z]\>[[:space:]]\+\<[b-qsu-z]\{4\}\>"
            r"[[:space:]]\+\<[b-qsu-z]\{2\}\>[[:space:]]\+\<a\>"
            r"[[:space:]]\+\<[b-qsu-z]\{5\}\>,",
            "-x", "a", "-x", "t",
        )

    def test_leading_punctuation(self):
        self.check("' _ _", r"'\<[[:lower:]]\{2\}\>")

    def test_interior_punctuation_stays_inside(self):
        self.check("_ _ _ ' _", r"\<[[:lower:]]\{3\}'[[:lower:]]\>")

    def test_leading_and_interior_punctuation(self):
        self.check(
            "' _ _ _ _ _ ' _", r"'\<[[:lower:]]\{5\}'[[:lower:]]\>"
        )

    def test_punctuation_only_word(self):
        self.check(
            "- / _ _", r"-[[:space:]]\+\<[[:lower:]]\{2\}\>"
        )

    def test_trailing_period_is_escaped_and_outside(self):
        self.check("_ _ .", r"\<[[:lower:]]\{2\}\>\.")


if __name__ == "__main__":
    unittest.main()
