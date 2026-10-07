#!/usr/bin/env python
"""Check the layout of skills/.

- SKILL.md may only live at the skills/<category>/<name>/SKILL.md depth
- every skills/<category>/<name>/ directory must contain a SKILL.md
- the frontmatter name is required, must match the directory name, and must follow the naming rules
- the frontmatter description is required and must not be empty
- allowed-tools must be a string, not an array (gh skill validation requirement)
- a skill must not call a user-invoked skill (disable-model-invocation: true) through the Skill tool
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_CALL_RE = re.compile(
    r"Skill\(([a-z0-9-]+)\)|Skill tool(?:で| with) [`\"]([a-z0-9-]+)[`\"]"
)

errors: list[str] = []


def check_frontmatter(skill_md: Path) -> None:
    """Validate the frontmatter of a SKILL.md and append violations to errors.

    Args:
        skill_md: Path to the SKILL.md to check.
    """
    rel = skill_md.relative_to(ROOT)
    m = re.match(r"\A---\n(.*?)\n---\n", skill_md.read_text(), re.DOTALL)
    if not m:
        errors.append(f"{rel}: missing frontmatter (--- ... ---)")
        return
    fm = m.group(1)

    name = re.search(r"^name:[ \t]*(.*)$", fm, re.MULTILINE)
    if not name or not name.group(1).strip():
        errors.append(f"{rel}: missing name")
    else:
        value = name.group(1).strip()
        if value != skill_md.parent.name:
            errors.append(
                f"{rel}: name '{value}' does not match directory name '{skill_md.parent.name}'"
            )
        if not NAME_RE.match(value) or len(value) > 64:
            errors.append(
                f"{rel}: name '{value}' violates naming rules (lowercase alphanumerics and hyphens, max 64 chars)"
            )

    desc = re.search(r"^description:[ \t]*(.*)$", fm, re.MULTILINE)
    if not desc:
        errors.append(f"{rel}: missing description")
    elif desc.group(1).strip() in {"", ">", ">-", "|", "|-"} and not re.match(
        r"\n[ \t]+\S", fm[desc.end() :]
    ):
        errors.append(f"{rel}: description is empty")

    if re.search(r"^allowed-tools:[ \t]*(?:\[|\n[ \t]*-[ \t])", fm, re.MULTILINE):
        errors.append(f"{rel}: allowed-tools must be a string, not an array")


def check_skill_calls(skill_mds: list[Path]) -> None:
    """Report Skill tool calls to user-invoked skills, which the tool cannot load.

    Args:
        skill_mds: Paths to every SKILL.md in the repository.
    """
    user_invoked = {
        md.parent.name
        for md in skill_mds
        if re.search(
            r"^disable-model-invocation:[ \t]*true[ \t]*$", md.read_text(), re.MULTILINE
        )
    }
    for md in skill_mds:
        for m in SKILL_CALL_RE.finditer(md.read_text()):
            name = m.group(1) or m.group(2)
            if name in user_invoked:
                errors.append(
                    f"{md.relative_to(ROOT)}: calls user-invoked skill '{name}' through the Skill tool; ask the user to run it instead"
                )


def main() -> None:
    """Run all layout checks and exit with 1 if any violation is found."""
    if (ROOT / "SKILL.md").exists():
        errors.append(
            "SKILL.md: not allowed at the repository root; it would hide every other skill from discovery"
        )

    for md in ROOT.glob("skills/**/SKILL.md"):
        if len(md.relative_to(ROOT).parts) != 4:
            errors.append(
                f"{md.relative_to(ROOT)}: not at the skills/<category>/<name>/SKILL.md depth"
            )

    for category in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        for skill_dir in sorted(p for p in category.iterdir() if p.is_dir()):
            if (skill_dir / "SKILL.md").exists():
                check_frontmatter(skill_dir / "SKILL.md")
            else:
                errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")

    check_skill_calls(sorted(ROOT.glob("skills/*/*/SKILL.md")))

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("layout ok")


if __name__ == "__main__":
    main()
