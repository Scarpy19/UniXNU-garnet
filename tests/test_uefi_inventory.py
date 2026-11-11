"""Test the reference-only firmware dependency inventory."""

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/inventory-uefi-inputs.py"
spec = importlib.util.spec_from_file_location("uefi_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class UefiInventoryTests(unittest.TestCase):
    def test_only_garnet_binary_inf_lines_and_deduplication(self):
        text = """
  INF Binaries/garnet/QcomPkg/Drivers/Example/Example.inf
  INF Binaries/garnet/QcomPkg/Drivers/Example/Example.inf # duplicate
  # INF Binaries/garnet/Ignored.inf
  INF MdeModulePkg/Universal/Other.inf
!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1
  INF Binaries/garnet/QcomPkg/Drivers/Display/Display.inf
!endif
"""
        self.assertEqual(inventory.referenced_infs(text), [
            "Binaries/garnet/QcomPkg/Drivers/Display/Display.inf",
            "Binaries/garnet/QcomPkg/Drivers/Example/Example.inf",
        ])

    def test_empty_input(self):
        self.assertEqual(inventory.referenced_infs("# no driver\n"), [])
        self.assertEqual(inventory.referenced_raw_files("# no raw files\n"), [])

    def test_raw_entries_and_comments(self):
        text = """
  SECTION RAW = Binaries/garnet/RawFiles/Example.cfg
  # SECTION RAW = Binaries/garnet/RawFiles/Ignored.cfg
  SECTION RAW = Binaries/garnet/RawFiles/Example.cfg # duplicate
"""
        self.assertEqual(inventory.referenced_raw_files(text), ["Binaries/garnet/RawFiles/Example.cfg"])


if __name__ == "__main__":
    unittest.main()
