import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_public_profile.py"
SPEC = importlib.util.spec_from_file_location("check_public_profile", MODULE_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PublicProfileChecks(unittest.TestCase):
    def test_detects_high_confidence_secret_without_returning_value(self) -> None:
        secret = "ghp_" + "A" * 36
        findings = CHECKER.scan_text(f"token={secret}")
        self.assertEqual(findings, {"GitHub token"})
        self.assertNotIn(secret, " ".join(findings))

    def test_detects_private_network_and_local_path(self) -> None:
        private_address = "http://192" + ".168.1.20"
        local_path = "/home" + "/alice/private.txt"
        findings = CHECKER.scan_text(f"{private_address} {local_path}")
        self.assertEqual(findings, {"private IPv4 address", "local home path"})

    def test_allows_documentation_placeholders(self) -> None:
        self.assertEqual(CHECKER.scan_text("/home/user/project /home/runner/work"), set())

    def test_extracts_unique_http_links_and_skips_images(self) -> None:
        markdown = "[Site](https://example.com) [Again](https://example.com) ![Logo](https://example.com/logo.png)"
        self.assertEqual(CHECKER.extract_links(markdown), ["https://example.com"])


if __name__ == "__main__":
    unittest.main()
