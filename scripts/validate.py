#!/usr/bin/env python3
"""Validate the repository's Agent Skill and Codex plugin distribution."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TOP_LEVEL_KEY_RE = re.compile(r"^(?P<key>[a-zA-Z][a-zA-Z0-9_-]*):(?:\s*(?P<value>.*))?$")
NESTED_KEY_RE = re.compile(r"^  (?P<key>[^:#]+):\s*(?P<value>.*)$")


@dataclass(frozen=True)
class Layout:
    root: Path
    plugin: Path
    skill: Path
    skill_md: Path
    openai_yaml: Path
    plugin_json: Path
    marketplace_json: Path
    evals_json: Path

    @classmethod
    def from_root(cls, root: Path) -> "Layout":
        root = root.resolve()
        plugin = root / "plugins" / "subagents-workflow"
        skill = plugin / "skills" / "subagents-workflow"
        return cls(root, plugin, skill, skill / "SKILL.md", skill / "agents" / "openai.yaml", plugin / ".codex-plugin" / "plugin.json", root / ".agents" / "plugins" / "marketplace.json", skill / "evals" / "evals.json")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("SKILL.md must start with closed YAML frontmatter")
    result: dict[str, Any] = {}
    current_map: str | None = None
    for line_number, line in enumerate(match.group("yaml").splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        nested = NESTED_KEY_RE.match(line)
        if nested:
            if current_map is None:
                raise ValueError(f"unexpected nested field on line {line_number}")
            result.setdefault(current_map, {})[nested.group("key").strip()] = unquote(nested.group("value"))
            continue
        top = TOP_LEVEL_KEY_RE.match(line)
        if not top:
            raise ValueError(f"unsupported frontmatter syntax on line {line_number}")
        key = top.group("key")
        raw_value = (top.group("value") or "").strip()
        if raw_value:
            result[key] = unquote(raw_value)
            current_map = None
        else:
            result[key] = {}
            current_map = key
    return result, text[match.end():]


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing required JSON file: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return None
    return value


def require_file(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing required file: {path}")


def validate_relative_links(markdown_path: Path, text: str, errors: list[str]) -> None:
    for raw_target in LINK_RE.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("#", "mailto:")):
            continue
        if not (markdown_path.parent / target).resolve().exists():
            errors.append(f"broken relative link in {markdown_path}: {raw_target}")


def validate_skill(layout: Layout, errors: list[str]) -> dict[str, Any] | None:
    require_file(layout.skill_md, errors)
    require_file(layout.openai_yaml, errors)
    if not layout.skill_md.is_file():
        return None
    text = layout.skill_md.read_text(encoding="utf-8")
    try:
        frontmatter, body = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        return None
    allowed = {"name", "description", "license", "metadata", "allowed-tools"}
    unexpected = sorted(set(frontmatter) - allowed)
    if unexpected:
        errors.append(f"unsupported SKILL.md frontmatter fields: {', '.join(unexpected)}")
    name = frontmatter.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append("SKILL.md name must be lowercase hyphen-case and at most 64 characters")
    elif name != layout.skill.name:
        errors.append("SKILL.md name must match its parent directory")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md description must be non-empty")
    elif len(description) > 1024:
        errors.append("SKILL.md description must be at most 1024 characters")
    if frontmatter.get("license") != "MIT":
        errors.append("SKILL.md license must be MIT")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict) or not metadata:
        errors.append("SKILL.md metadata must be a non-empty string map")
    elif not all(isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()):
        errors.append("SKILL.md metadata values must all be strings")
    elif not metadata.get("compatibility") or len(metadata["compatibility"]) > 500:
        errors.append("SKILL.md metadata.compatibility must be 1-500 characters")
    if len(text.splitlines()) >= 500:
        errors.append("SKILL.md should stay under 500 lines")
    if not body.strip():
        errors.append("SKILL.md must contain instruction body content")
    validate_relative_links(layout.skill_md, text, errors)
    if layout.openai_yaml.is_file():
        agent_yaml = layout.openai_yaml.read_text(encoding="utf-8")
        if "$subagents-workflow" not in agent_yaml:
            errors.append("agents/openai.yaml default_prompt must mention $subagents-workflow")
        if "allow_implicit_invocation: true" not in agent_yaml:
            errors.append("agents/openai.yaml must enable implicit invocation")
        short_match = re.search(r'^  short_description:\s*"([^"]+)"\s*$', agent_yaml, re.MULTILINE)
        if not short_match or not 25 <= len(short_match.group(1)) <= 64:
            errors.append("agents/openai.yaml short_description must be 25-64 characters")
    return frontmatter


def validate_plugin(layout: Layout, frontmatter: dict[str, Any] | None, errors: list[str]) -> str | None:
    manifest = load_json(layout.plugin_json, errors)
    if manifest is None:
        return None
    if manifest.get("name") != "subagents-workflow":
        errors.append("plugin name must be subagents-workflow")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        errors.append("plugin version must be strict Semantic Versioning")
        version = None
    if manifest.get("skills", "").rstrip("/") != "./skills":
        errors.append("plugin skills path must be ./skills/")
    if manifest.get("license") != "MIT":
        errors.append("plugin license must be MIT")
    author = manifest.get("author")
    if not isinstance(author, dict) or not author.get("name"):
        errors.append("plugin author.name is required")
    interface = manifest.get("interface")
    required_interface = {"displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"}
    if not isinstance(interface, dict):
        errors.append("plugin interface object is required")
    else:
        missing = sorted(required_interface - set(interface))
        if missing:
            errors.append(f"plugin interface missing: {', '.join(missing)}")
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
            errors.append("plugin interface.defaultPrompt must contain 1-3 prompts")
        elif any(not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128 for prompt in prompts):
            errors.append("plugin default prompts must be non-empty strings up to 128 characters")
    if frontmatter and version:
        metadata = frontmatter.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get("version") != version:
            errors.append("SKILL.md metadata.version must match plugin version")
    return version


def validate_marketplace(layout: Layout, errors: list[str]) -> None:
    marketplace = load_json(layout.marketplace_json, errors)
    if marketplace is None:
        return
    if marketplace.get("name") != "eldenpdx":
        errors.append("marketplace name must be eldenpdx")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append("marketplace must contain exactly one plugin")
        return
    entry = plugins[0]
    if not isinstance(entry, dict) or entry.get("name") != "subagents-workflow":
        errors.append("marketplace plugin entry must be subagents-workflow")
        return
    if entry.get("source") != {"source": "local", "path": "./plugins/subagents-workflow"}:
        errors.append("marketplace source must point to ./plugins/subagents-workflow")
    if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        errors.append("marketplace policy must declare AVAILABLE and ON_INSTALL")


def validate_evals(layout: Layout, errors: list[str]) -> None:
    payload = load_json(layout.evals_json, errors)
    if payload is None:
        return
    if payload.get("skill_name") != "subagents-workflow":
        errors.append("evals skill_name must be subagents-workflow")
    evals = payload.get("evals")
    if not isinstance(evals, list) or len(evals) < 3:
        errors.append("evals.json must contain at least three cases")
        return
    ids: set[Any] = set()
    for case in evals:
        if not isinstance(case, dict):
            errors.append("each eval case must be an object")
            continue
        case_id = case.get("id")
        if case_id in ids:
            errors.append(f"duplicate eval id: {case_id}")
        ids.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"eval {case_id} has an empty prompt")
        if not isinstance(case.get("expected_output"), str) or not case["expected_output"].strip():
            errors.append(f"eval {case_id} has an empty expected_output")


def validate_repository(root: Path) -> list[str]:
    layout = Layout.from_root(root)
    errors: list[str] = []
    for path in (layout.root / "README.md", layout.root / "README.zh-CN.md", layout.root / "README.ja.md", layout.root / "SKILL.md", layout.root / "agents" / "openai.yaml", layout.root / "LICENSE", layout.root / "CHANGELOG.md", layout.root / "CONTRIBUTING.md", layout.root / "SECURITY.md", layout.plugin / "README.md", layout.plugin / "LICENSE"):
        require_file(path, errors)
    frontmatter = validate_skill(layout, errors)
    version = validate_plugin(layout, frontmatter, errors)
    validate_marketplace(layout, errors)
    validate_evals(layout, errors)
    if (layout.root / "LICENSE").is_file() and (layout.plugin / "LICENSE").is_file() and (layout.root / "LICENSE").read_bytes() != (layout.plugin / "LICENSE").read_bytes():
        errors.append("root and plugin LICENSE files must be identical")
    if version and (layout.root / "CHANGELOG.md").is_file() and f"## [{version}] - " not in (layout.root / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append("CHANGELOG.md must contain the current plugin version")
    root_skill_path = layout.root / "SKILL.md"
    if root_skill_path.is_file():
        root_skill_text = root_skill_path.read_text(encoding="utf-8")
        try:
            root_frontmatter, _ = parse_frontmatter(root_skill_text)
        except ValueError as exc:
            errors.append(f"root SKILL.md: {exc}")
        else:
            if root_frontmatter.get("name") != "subagents-workflow":
                errors.append("root SKILL.md name must be subagents-workflow")
            root_metadata = root_frontmatter.get("metadata")
            if not isinstance(root_metadata, dict) or root_metadata.get("version") != version:
                errors.append("root SKILL.md metadata.version must match plugin version")
            if not isinstance(root_metadata, dict) or root_metadata.get("canonical-path") != "plugins/subagents-workflow/skills/subagents-workflow/SKILL.md":
                errors.append("root SKILL.md must declare the canonical Skill path")
            if frontmatter and root_frontmatter.get("description") != frontmatter.get("description"):
                errors.append("root and canonical SKILL.md descriptions must match")
        validate_relative_links(root_skill_path, root_skill_text, errors)
    root_agent_yaml = layout.root / "agents" / "openai.yaml"
    if root_agent_yaml.is_file() and layout.openai_yaml.is_file() and root_agent_yaml.read_bytes() != layout.openai_yaml.read_bytes():
        errors.append("root and canonical agents/openai.yaml files must be identical")
    readme_path = layout.root / "README.md"
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        for fragment in ("https://github.com/EldenPdx/subagents-workflow", "plugins/subagents-workflow/skills/subagents-workflow", "codex plugin marketplace add EldenPdx/subagents-workflow"):
            if fragment not in readme:
                errors.append(f"README.md missing required installation fragment: {fragment}")
        validate_relative_links(readme_path, readme, errors)
    localized_readmes = {
        layout.root / "README.md": "**English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)",
        layout.root / "README.zh-CN.md": "[English](README.md) | **简体中文** | [日本語](README.ja.md)",
        layout.root / "README.ja.md": "[English](README.md) | [简体中文](README.zh-CN.md) | **日本語**",
    }
    for localized_path, expected_navigation in localized_readmes.items():
        if not localized_path.is_file():
            continue
        localized_text = localized_path.read_text(encoding="utf-8")
        if not localized_text.startswith(expected_navigation + "\n"):
            errors.append(f"{localized_path.name} must start with the standard language navigation")
        for fragment in ("codex plugin marketplace add EldenPdx/subagents-workflow", "plugins/subagents-workflow/skills/subagents-workflow"):
            if fragment not in localized_text:
                errors.append(f"{localized_path.name} missing required installation fragment: {fragment}")
        validate_relative_links(localized_path, localized_text, errors)
    for path in layout.root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name == ".DS_Store":
            errors.append(f"forbidden macOS metadata file: {path}")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".yml", ".py"} and ("[TODO" + ":") in path.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"unfinished scaffold placeholder in {path}")
    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed: {root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
