#!/usr/bin/env python
"""Check consistency between the plugin manifests and skills/.

- the skills list in .claude-plugin/plugin.json exactly matches the filesystem
- the skills path in .codex-plugin/plugin.json points to an existing directory
- the version fields of both plugin.json files match
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MANIFEST = ".claude-plugin/plugin.json"
CODEX_MANIFEST = ".codex-plugin/plugin.json"

errors: list[str] = []

claude = json.loads((ROOT / CLAUDE_MANIFEST).read_text())
codex = json.loads((ROOT / CODEX_MANIFEST).read_text())

actual = {
    f"./{p.parent.relative_to(ROOT).as_posix()}"
    for p in ROOT.glob("skills/*/*/SKILL.md")
}
listed = claude.get("skills", [])

for path in sorted(actual - set(listed)):
    errors.append(f"{CLAUDE_MANIFEST}: {path} is not listed in skills")
for path in sorted(set(listed) - actual):
    errors.append(f"{CLAUDE_MANIFEST}: {path} points to a nonexistent skill")
if len(listed) != len(set(listed)):
    errors.append(f"{CLAUDE_MANIFEST}: skills contains duplicates")

codex_skills = codex.get("skills", "")
if not (ROOT / codex_skills.removeprefix("./")).is_dir():
    errors.append(f"{CODEX_MANIFEST}: skills path '{codex_skills}' does not exist")

if claude.get("version") != codex.get("version"):
    errors.append(
        f"version mismatch: {CLAUDE_MANIFEST}={claude.get('version')} {CODEX_MANIFEST}={codex.get('version')}"
    )

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("plugin manifest ok")
