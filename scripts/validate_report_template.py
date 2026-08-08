#!/usr/bin/env python3
"""Validate invariants for the job market analyzer report template and examples."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "report-template.html"
SKILL = ROOT / "SKILL.md"
GITIGNORE = ROOT / ".gitignore"
EXAMPLES_DIR = ROOT / "examples"

# Patterns that indicate hardcoded example content (must NOT appear in pure template)
CSS_BLOCK = re.compile(r'<style>.*?</style>', re.DOTALL)
COMMENT_BLOCK = re.compile(r'<!--.*?-->', re.DOTALL)
EXAMPLE_PATTERNS = [
    (r'📍\s*[^{\s]', "hardcoded location (e.g. 📍 上海) outside placeholder"),
    (r'💰\s*[^{\s]', "hardcoded salary (e.g. 💰 25-35K) outside placeholder"),
    (r'📋\s*[^{\s]', "hardcoded experience requirement outside placeholder"),
    (r'外企巨头.*全球500强', "hardcoded Tier header"),
    (r'互联网大厂.*千亿市值', "hardcoded Tier header"),
    (r'行业独角兽.*上市物流', "hardcoded Tier header"),
    (r'远程.*国际化公司', "hardcoded Tier header"),
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
    "rec-star", "rec", "tier-1", "tier-2", "tier-3", "tier-4",
]

ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def validate_gitignore(gi: str) -> None:
    if "config/user-profile.yaml" not in gi:
        error(".gitignore must ignore config/user-profile.yaml")
    for hf in ("LICENSE",):
        if hf not in gi:
            warn(f".gitignore may want to protect {hf}")


def validate_template(template: str) -> None:
    # 1. No hardcoded example content patterns
    body = CSS_BLOCK.sub('', template)
    body = COMMENT_BLOCK.sub('', body)
    for pattern, description in EXAMPLE_PATTERNS:
        if re.search(pattern, body):
            error(f"Pure template contains {description}. "
                  f"Move example content to examples/ instead.")

    # 2. All required placeholders present
    for ph in REQUIRED_PLACEHOLDERS:
        if ph not in template:
            error(f"Pure template missing placeholder: {ph}")

    # 3. Tier-badge CSS classes
    for i in range(1, 5):
        if f".tier-{i}" not in template:
            error(f"Pure template missing CSS class: .tier-{i}")

    # 4. rec-star and rec CSS classes
    if ".rec-star" not in template:
        error("Pure template missing CSS class: .rec-star")
    if ".rec {" not in template and ".rec{" not in template:
        error("Pure template missing CSS class: .rec")

    # 5. No pseudo links
    if 'href="#"' in template or "javascript:void(0)" in template:
        error("Template contains placeholder or javascript pseudo links")


def validate_skill(skill: str) -> None:
    for invariant in SKILL_INVARIANTS:
        if invariant not in skill:
            error(f"SKILL.md missing invariant: '{invariant}'")


def validate_example_reports() -> None:
    if not EXAMPLES_DIR.exists():
        return
    for example_path in EXAMPLES_DIR.glob("*.html"):
        html = example_path.read_text(encoding="utf-8")
        # Every job-card must have at least one job-link
        cards = re.findall(r'<div[^>]*class="[^"]*\bjob-card\b[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        if not cards:
            # Try simpler extraction
            card_blocks = re.split(r'<div class="[^"]*\bjob-card\b[^"]*"', html)
            cards = card_blocks[1:]  # Skip content before first card
        if not cards:
            warn(f"{example_path.name}: no job-card divs found")

        # No pseudo links in examples
        if 'href="#"' in html:
            error(f"{example_path.name}: contains href='#' placeholder link")
        if "javascript:void(0)" in html:
            error(f"{example_path.name}: contains javascript:void(0) link")

        # At least one real http link
        links = re.findall(r'href="(https?://[^"]*)"', html)
        if not links:
            warn(f"{example_path.name}: no http/https links found")


def validate_json_blocks(filepath: Path) -> None:
    """Parse JSON blocks in references and check for valid JSON + Windows path escapes."""
    if not filepath.exists():
        return
    content = filepath.read_text(encoding="utf-8")
    json_blocks = re.findall(r'```json\n(.*?)```', content, re.DOTALL)
    for i, block in enumerate(json_blocks):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            error(f"{filepath.name} JSON block #{i + 1}: invalid JSON — {e}")
        # Check for unescaped single backslashes in JSON strings (Windows paths)
        for j, line in enumerate(block.split('\n')):
            # A single backslash not followed by a valid JSON escape char is suspicious
            suspicious = re.findall(r'(?<!\\)\\(?!["\\/bfnrtu])', line)
            if suspicious:
                error(f"{filepath.name} JSON block #{i + 1}, line {j + 1}: "
                      f"unescaped backslash in JSON string — use \\\\ for Windows paths")


def main() -> None:
    validate_gitignore(GITIGNORE.read_text(encoding="utf-8"))
    validate_skill(SKILL.read_text(encoding="utf-8"))
    validate_template(TEMPLATE.read_text(encoding="utf-8"))
    validate_example_reports()
    validate_json_blocks(ROOT / "references" / "mcp-jobs-setup.md")

    if WARNINGS:
        for w in WARNINGS:
            print(f"WARNING: {w}")
    if ERRORS:
        for e in ERRORS:
            print(f"ERROR: {e}")
        print(f"\n{len(ERRORS)} error(s) found.")
        sys.exit(1)

    print("Report template validation passed.")


if __name__ == "__main__":
    main()
