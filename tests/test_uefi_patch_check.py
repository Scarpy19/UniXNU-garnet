"""Ensure the UEFI patch checker fails closed on uncertain source state."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check-uefi-patch.py"
spec = importlib.util.spec_from_file_location("uefi_patch_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def result(stdout="", stderr="", code=0):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=code)


class UefiPatchCheckTests(unittest.TestCase):
    @patch.object(checker, "git")
    def test_rejects_unknown_revision(self, git):
        git.return_value = result("0" * 40)
        self.assertFalse(checker.check(Path("unused"))[0])
        self.assertEqual(git.call_count, 1)

    @patch.object(checker, "git")
    def test_rejects_dirty_sources(self, git):
        git.side_effect = [result(next(iter(checker.SUPPORTED))), result(" M platform.dsc")]
        self.assertFalse(checker.check(Path("unused"))[0])
        self.assertEqual(git.call_count, 2)

    @patch.object(checker, "git")
    def test_fails_when_patch_does_not_apply(self, git):
        git.side_effect = [result(next(iter(checker.SUPPORTED))), result(), result(stderr="conflict", code=1)]
        self.assertFalse(checker.check(Path("unused"))[0])

    @patch.object(checker, "git")
    def test_reports_textual_success(self, git):
        git.side_effect = [result(next(iter(checker.SUPPORTED))), result(), result()]
        ok, message = checker.check(Path("unused"))
        self.assertTrue(ok)
        self.assertIn("not built or verified", message)


if __name__ == "__main__":
    unittest.main()
