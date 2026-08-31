from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package import package_repository  # noqa: E402


class PackageRepositoryTests(unittest.TestCase):
    def test_builds_plugin_and_skill_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plugin_zip, skill_zip = package_repository(ROOT, Path(temp))
            self.assertTrue(plugin_zip.is_file())
            self.assertTrue(skill_zip.is_file())

            with ZipFile(plugin_zip) as archive:
                names = set(archive.namelist())
                self.assertIn(".codex-plugin/plugin.json", names)
                self.assertIn("skills/subagents-workflow/SKILL.md", names)

            with ZipFile(skill_zip) as archive:
                names = set(archive.namelist())
                self.assertIn("subagents-workflow/SKILL.md", names)
                self.assertIn("subagents-workflow/agents/openai.yaml", names)


if __name__ == "__main__":
    unittest.main()
