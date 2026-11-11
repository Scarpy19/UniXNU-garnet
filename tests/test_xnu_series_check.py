"""Tests for source and series validation without downloading XNU."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check-xnu-series.py"
spec = importlib.util.spec_from_file_location("xnu_series_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class XnuSeriesCheckTests(unittest.TestCase):
    def test_diagnostic_skip_is_explicit_and_rejects_ambiguity(self):
        patches = [Path("/a/one.patch"), Path("/a/two.patch")]
        self.assertEqual(checker.diagnostic_skip(patches, ["one.patch"]), [patches[1]])
        for invalid in (["missing.patch"], ["one.patch", "two.patch"]):
            with self.assertRaises(ValueError):
                checker.diagnostic_skip(patches, invalid)
        with self.assertRaises(ValueError):
            checker.diagnostic_skip([Path("/a/one.patch"), Path("/b/one.patch")], ["one.patch"])

    def test_rejects_missing_source(self):
        with self.assertRaises(ValueError):
            checker.selected_inputs({"modules": [], "patch_order": []})

    def test_rejects_wrong_pin(self):
        status = {"modules": [{"kind": "refer", "name": "xnu", "path": "/xnu", "pin": "wrong"}], "patch_order": []}
        with self.assertRaises(ValueError):
            checker.selected_inputs(status)

    def test_requires_existing_patch_and_returns_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            patch = Path(temp) / "example.patch"
            patch.write_text("test", encoding="utf-8")
            status = {"modules": [{"kind": "refer", "name": "xnu", "path": "/xnu", "pin": checker.EXPECTED_XNU}], "patch_order": [str(patch)]}
            self.assertEqual(checker.selected_inputs(status), (Path("/xnu"), [patch]))
            status["patch_order"] = [str(patch / "missing")]
            with self.assertRaises(ValueError):
                checker.selected_inputs(status)


if __name__ == "__main__":
    unittest.main()
