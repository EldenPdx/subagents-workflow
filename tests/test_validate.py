from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_validate", ROOT / "scripts" / "validate.py")
assert SPEC and SPEC.loader
repo_validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = repo_validate
SPEC.loader.exec_module(repo_validate)


class ValidateRepositoryTests(unittest.TestCase):
    def copy_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", ".serena", "dist", "__pycache__", ".DS_Store"),
        )
        return temp, target

    def test_current_repository_is_valid(self) -> None:
        self.assertEqual(repo_validate.validate_repository(ROOT), [])

    def test_detects_skill_name_mismatch(self) -> None:
        temp, target = self.copy_repo()
        self.addCleanup(temp.cleanup)
        skill = target / "plugins/subagents-workflow/skills/subagents-workflow/SKILL.md"
        skill.write_text(skill.read_text().replace("name: subagents-workflow", "name: wrong-name", 1))
        errors = repo_validate.validate_repository(target)
        self.assertTrue(any("parent directory" in error for error in errors), errors)

    def test_detects_version_mismatch(self) -> None:
        temp, target = self.copy_repo()
        self.addCleanup(temp.cleanup)
        manifest = target / "plugins/subagents-workflow/.codex-plugin/plugin.json"
        payload = json.loads(manifest.read_text())
        payload["version"] = "1.0.1"
        manifest.write_text(json.dumps(payload, indent=2) + "\n")
        errors = repo_validate.validate_repository(target)
        self.assertTrue(any("metadata.version" in error for error in errors), errors)

    def test_detects_broken_reference(self) -> None:
        temp, target = self.copy_repo()
        self.addCleanup(temp.cleanup)
        reference = target / "plugins/subagents-workflow/skills/subagents-workflow/references/contracts.md"
        reference.unlink()
        errors = repo_validate.validate_repository(target)
        self.assertTrue(any("broken relative link" in error for error in errors), errors)

    def test_detects_missing_localized_readme(self) -> None:
        temp, target = self.copy_repo()
        self.addCleanup(temp.cleanup)
        (target / "README.ja.md").unlink()
        errors = repo_validate.validate_repository(target)
        self.assertTrue(any("README.ja.md" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
