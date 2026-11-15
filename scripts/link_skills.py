#!/usr/bin/env python
"""Link every skill into .claude/skills/ and .agents/skills/.

Claude Code reads project skills from .claude/skills/<name>/ and Codex from
.agents/skills/<name>/, so each skills/<category>/<name>/ gets one symlink per
directory. Symlinks whose skill was removed or renamed are deleted.

Exits with 1 when any link changed. prek does not treat newly created untracked
files as a modification, so without this a missing link would pass CI.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_DIRS = [ROOT / ".claude" / "skills", ROOT / ".agents" / "skills"]

targets = {
    md.parent.name: Path("../..") / md.parent.relative_to(ROOT)
    for md in ROOT.glob("skills/*/*/SKILL.md")
}
changed: list[str] = []

for link_dir in LINK_DIRS:
    link_dir.mkdir(parents=True, exist_ok=True)
    for link in link_dir.iterdir():
        if link.is_symlink() and link.readlink() != targets.get(link.name):
            link.unlink()
            changed.append(f"removed {link.relative_to(ROOT)}")
    for name, target in targets.items():
        link = link_dir / name
        if not link.is_symlink():
            link.symlink_to(target, target_is_directory=True)
            changed.append(f"linked {link.relative_to(ROOT)} -> {target}")

if changed:
    print("\n".join(changed))
    sys.exit(1)
