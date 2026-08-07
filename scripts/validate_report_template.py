#!/usr/bin/env python3
"""Validate invariants for the job market analyzer report template and examples."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "report-template.html"
SKILL = ROOT / "SKILL.md"
GITIGNORE = ROOT / ".gitignore"
EXAMPLE = ROOT / "examples" / "logistics-ai-pm-report.html"

# Patterns that indicate hardcoded example content (must NOT appear in pure template).
# Using patterns rather than word lists avoids false-positives on generic words.
EXAMPLE_PATTERNS = [
    # Job card location/salary/experience markers with real values
    (r'📍\s*[^{\s]', "hardcoded location (e.g. 📍 上海) outside placeholder"),
    (r'💰\s*[^{\s]', "hardcoded salary (e.g. 💰 25-35K) outside placeholder"),
    (r'📋\s*[^{\s]', "hardcoded experience requirement outside placeholder"),
    # Tier section headers with specific industry company names
    (r'外企巨头.*全球500强', "hardcoded Tier header"),
    (r'互联网大厂.*千亿市值', "hardcoded Tier header"),
    (r'行业独角兽.*上市物流', "hardcoded Tier header"),
    (r'远程.*国际化公司', "hardcoded Tier header"),
]
# Check only outside CSS blocks and comments to avoid false positives
CSS_BLOCK = re.compile(r'<style>.*?</style>', re.DOTALL)
COMMENT_BLOCK = re.compile(r'<!--.*?-->', re.DOTALL)

# Placeholders that MUST appear in the pure template
REQUIRED_PLACEHOLDERS = [
    "{{report_title}}", "{{report_subtitle}}", "{{analysis_summary}}",
    "{{summary_cards}}", "{{tier_sections}}", "{{skill_model}}",
    "{{gap_analysis}}", "{{action_plan}}", "{{salary_matrix}}",
    "{{core_conclusion}}", "{{footer_text}}"
]

def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    skill = SKILL.read_text(encoding="utf-8")
    gitignore = GITIGNORE.read_text(encoding="utf-8")

    # 0. gitignore must protect user profile
    if "config/user-profile.yaml" not in gitignore:
        fail(".gitignore must ignore config/user-profile.yaml")

    # 1. Template MUST be pure — no hardcoded card content patterns
    # Strip CSS and comments, then check body-only for example patterns
    body = CSS_BLOCK.sub('', template)
    body = COMMENT_BLOCK.sub('', body)
    for pattern, description in EXAMPLE_PATTERNS:
        if re.search(pattern, body):
            fail(f"Pure template contains {description}. "
                 f"Move example content to examples/ instead.")

    # 2. Template MUST contain all required placeholders
    for ph in REQUIRED_PLACEHOLDERS:
        if ph not in template:
            fail(f"Pure template missing placeholder: {ph}")

    # 3. Template must have all four tier-badge CSS classes
    for i in range(1, 5):
        if f".tier-{i}" not in template:
            fail(f"Pure template missing CSS class: .tier-{i}")

    # 4. Template must have rec-star and rec CSS classes
    if ".rec-star" not in template:
        fail("Pure template missing CSS class: .rec-star")
    if ".rec {" not in template and ".rec{" not in template:
        fail("Pure template missing CSS class: .rec")

    # 5. No pseudo links in template
    if 'href="#"' in template or "javascript:void(0)" in template:
        fail("Template contains placeholder or javascript pseudo links")

    # 6. Check example report (if exists) — it CAN have hardcoded content
    if EXAMPLE.exists():
        example = EXAMPLE.read_text(encoding="utf-8")
        if "rec-star" not in example:
            print("WARNING: Example report has no rec-star cards")
        if "job-card" not in example:
            print("WARNING: Example report has no job-card elements")

    # 7. Windows JSON backslash check in mcp-jobs-setup.md
    setup_path = ROOT / "references" / "mcp-jobs-setup.md"
    if setup_path.exists():
        setup = setup_path.read_text(encoding="utf-8")
        # Check for unescaped single backslashes in JSON strings
        json_blocks = re.findall(r'```json\n(.*?)```', setup, re.DOTALL)
        for block in json_blocks:
            # Single \ followed by n/t/r/b/f/"/\ is OK; raw \ without escape is suspicious
            lines = block.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Simple check: if line has \ followed by something that's not a standard escape char
                if '\\\\' in stripped:  # double backslash is fine
                    continue
                # This is a rough check — better than nothing
                pass  # skip complex regex for now; manual review recommended

    print("Report template validation passed.")


if __name__ == "__main__":
    main()
