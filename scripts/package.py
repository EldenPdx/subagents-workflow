#!/usr/bin/env python3
"""Build deterministic ZIP archives for the plugin and standalone skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from validate import Layout, validate_repository

FIXED_TIMESTAMP = (2026, 8, 31, 0, 0, 0)
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts):
            yield path


def add_file(archive: ZipFile, source: Path, archive_name: str) -> None:
    info = ZipInfo(archive_name, FIXED_TIMESTAMP)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, source.read_bytes())


def write_archive(output: Path, source_root: Path, prefix: str = "") -> None:
    with ZipFile(output, "w") as archive:
        for source in iter_files(source_root):
            relative = source.relative_to(source_root).as_posix()
            add_file(archive, source, f"{prefix}{relative}" if prefix else relative)


def package_repository(root: Path, output_dir: Path) -> tuple[Path, Path]:
    errors = validate_repository(root)
    if errors:
        raise ValueError("repository validation failed:\n- " + "\n- ".join(errors))

    layout = Layout.from_root(root)
    version = json.loads(layout.plugin_json.read_text(encoding="utf-8"))["version"]
    output_dir.mkdir(parents=True, exist_ok=True)

    plugin_zip = output_dir / f"subagents-workflow-plugin-{version}.zip"
    skill_zip = output_dir / f"subagents-workflow-skill-{version}.zip"
    plugin_zip.unlink(missing_ok=True)
    skill_zip.unlink(missing_ok=True)

    write_archive(plugin_zip, layout.plugin)
    write_archive(skill_zip, layout.skill, prefix="subagents-workflow/")
    return plugin_zip, skill_zip


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist",
        help="Directory for generated archives (default: ./dist)",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        plugin_zip, skill_zip = package_repository(root, args.output_dir.resolve())
    except ValueError as exc:
        print(exc)
        return 1
    print(plugin_zip)
    print(skill_zip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
