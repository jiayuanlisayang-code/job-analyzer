#!/usr/bin/env python3

"""Validate invariants for the job market analyzer report template."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "report-template.html"
SKILL = ROOT / "SKILL.md"
GITIGNORE = ROOT / ".gitignore"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def section_between(text: str, start_marker: str, end_marker: str | None) -> str:
    try:
        start = text.index(start_marker)
    except ValueError:
        fail(f"Missing section marker: {start_marker}")
    if end_marker is None:
        return text[start:]
    try:
        end = text.index(end_marker, start)
    except ValueError:
        fail(f"Missing section marker: {end_marker}")
    return text[start:end]


def card_classes(section: str) -> list[str]:
    return re.findall(r'<div\s+class="([^"]*\bjob-card\b[^"]*)"', section)


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    skill = SKILL.read_text(encoding="utf-8")
    gitignore = GITIGNORE.read_text(encoding="utf-8")

    if "config/user-profile.yaml" not in gitignore:
        fail(".gitignore must ignore config/user-profile.yaml")

    if "**🚨 关键原则：检测到 mcp-jobs 不可用时，**" in skill:
        fail("SKILL.md contains broken nested bold syntax in the mcp-jobs principle")

    if 'href="#"' in template or "javascript:void(0)" in template:
        fail("Template contains placeholder or javascript pseudo links")

    tier1 = section_between(template, "<!-- ======= Tier 1:", "<!-- ======= Tier 2:")
    tier1_classes = card_classes(tier1)
    if not tier1_classes:
        fail("Tier 1 section must contain at least one job card")
    invalid_tier1 = [cls for cls in tier1_classes if "rec-star" not in cls.split()]
    if invalid_tier1:
        fail(f"Tier 1 job cards must use rec-star: {invalid_tier1}")

    if "<!-- ======= Tier 2:" in template:
        tier2 = section_between(template, "<!-- ======= Tier 2:", "<!-- ======= Tier 3:" if "<!-- ======= Tier 3:" in template else None)
        tier2_classes = card_classes(tier2)
        invalid_tier2 = [cls for cls in tier2_classes if "rec" not in cls.split()]
        if invalid_tier2:
            fail(f"Tier 2 job cards must use rec: {invalid_tier2}")

    print("Report template validation passed.")


if __name__ == "__main__":
    main()
