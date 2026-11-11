"""Safety and consistency checks for the incomplete garnet scaffold."""

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.board = tomllib.loads((ROOT / "board.toml").read_text(encoding="utf-8"))
        self.feeds = tomllib.loads((ROOT / "feeds.toml").read_text(encoding="utf-8"))

    def test_incomplete_board_is_guarded(self):
        self.assertIs(self.board["board"]["example"], True)
        self.assertEqual(self.board["board"]["name"], "garnet")
        self.assertIn("cpus=1", self.board["payload"]["kernel_args"])
        self.assertNotIn("soc:patches/xnu/series", self.board["kernel"]["patch_series"])

    def test_soc_feed_is_immutable_and_matches_board(self):
        sources = self.feeds["source"]
        self.assertEqual(len(sources), 1)
        source = sources[0]
        self.assertEqual(source["name"], self.board["board"]["soc_source"])
        self.assertEqual(source["kind"], "soc")
        self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")

    def test_uefi_candidate_remains_guarded_and_has_source_paths(self):
        firmware = self.board["firmware"]
        self.assertEqual(firmware["config"], "garnet")
        self.assertEqual(firmware["dsc"], "Platforms/Xiaomi/garnetPkg/garnet.dsc")
        self.assertIn("Binaries", firmware["submodules"])
        self.assertIn("{tree}/drivers/DarwinBoot", firmware["packages"])
        self.assertIs(self.board["board"]["example"], True)

    def test_referenced_device_files_exist(self):
        self.assertTrue((ROOT / "configs" / self.board["kernel"]["defconfig"]).is_file())
        source = self.board["device_tree"]["source"]
        self.assertTrue(source.startswith("device:"))
        self.assertTrue((ROOT / source.removeprefix("device:")).is_file())
        self.assertTrue((ROOT / "patches/xnu/series").is_file())

    def test_uefi_patch_uses_inherited_platform_dependencies(self):
        patch = (ROOT / "patches/uefi/0001-garnet-unixnu-handoff.patch").read_text(encoding="utf-8")
        additions = [line for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]
        for module in ("UniXNU.inf", "UniXNUDxe.inf", "UniXNURamDiskDxe.inf", "DarwinBoot.inf"):
            self.assertEqual(sum(module in line for line in additions), 2, module)
        for inherited in ("DiskIoDxe.inf", "Fat.inf", "HobLib|", "FdtLib|"):
            self.assertFalse(any(inherited in line for line in additions), inherited)


if __name__ == "__main__":
    unittest.main()
