#!/usr/bin/env python3
"""Validate invariants for the job market analyzer report template."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "report-template.html"
SKILL = ROOT / "SKILL.md"
GITIGNORE = ROOT / ".gitignore"

CSS_BLOCK = re.compile(r'<style>.*?</style>', re.DOTALL)
COMMENT_BLOCK = re.compile(r'<!--.*?-->', re.DOTALL)

EXAMPLE_PATTERNS = [
    (r'📍\s*[^{\s]', "hardcoded location outside placeholder"),
    (r'💰\s*[^{\s]', "hardcoded salary outside placeholder"),
    (r'📋\s*[^{\s]', "hardcoded experience requirement outside placeholder"),
]

REQUIRED_PLACEHOLDERS = [
    "{{report_title}}", "{{report_subtitle}}", "{{analysis_summary}}",
    "{{summary_cards}}", "{{tier_sections}}", "{{skill_model}}",
    "{{gap_analysis}}", "{{action_plan}}", "{{salary_matrix}}",
    "{{core_conclusion}}", "{{footer_text}}"
]

SKILL_INVARIANTS = [
    "阶段零", "阶段一", "阶段二", "阶段三", "阶段四",
    "阶段五", "阶段六", "阶段七", "阶段八", "强制输出协议",
    "rec-star", "tier-1", "tier-2", "tier-3", "tier-4",
]

ERRORS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def check_json_blocks(filepath: Path) -> None:
    if not filepath.exists():
        return
    content = filepath.read_text(encoding="utf-8")
    blocks = re.findall(r'```json\n(.*?)```', content, re.DOTALL)
    for i, block in enumerate(blocks):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            error(f"{filepath.name} JSON block #{i + 1}: invalid — {e}")
        for j, line in enumerate(block.split('\n')):
            if re.search(r'(?<!\\)\\(?!["\\/bfnrtu])', line):
                error(f"{filepath.name} JSON #{i + 1} line {j + 1}: "
                      f"unescaped backslash in JSON — use \\\\ for Windows paths")


def main() -> None:
    # gitignore
    gi = GITIGNORE.read_text(encoding="utf-8")
    if "config/user-profile.yaml" not in gi:
        error(".gitignore must ignore config/user-profile.yaml")

    # SKILL.md invariants
    skill = SKILL.read_text(encoding="utf-8")
    for inv in SKILL_INVARIANTS:
        if inv not in skill:
            error(f"SKILL.md missing: '{inv}'")

    # Template purity
    template = TEMPLATE.read_text(encoding="utf-8")
    body = CSS_BLOCK.sub('', template)
    body = COMMENT_BLOCK.sub('', body)
    for pattern, desc in EXAMPLE_PATTERNS:
        if re.search(pattern, body):
            error(f"Template contains {desc}")

    for ph in REQUIRED_PLACEHOLDERS:
        if ph not in template:
            error(f"Template missing placeholder: {ph}")

    for i in range(1, 5):
        if f".tier-{i}" not in template:
            error(f"Template missing CSS: .tier-{i}")

    if ".rec-star" not in template:
        error("Template missing CSS: .rec-star")

    if 'href="#"' in template or "javascript:void(0)" in template:
        error("Template contains pseudo links")

    # JSON blocks in references
    check_json_blocks(ROOT / "references" / "mcp-jobs-setup.md")

    if ERRORS:
        for e in ERRORS:
            print(f"ERROR: {e}")
        print(f"\n{len(ERRORS)} error(s) found.")
        sys.exit(1)

    print("Report template validation passed.")


if __name__ == "__main__":
    main()
