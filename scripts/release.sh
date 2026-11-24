#!/usr/bin/env bash
# Release: sync the version into the plugin manifests and agents/apm.yml, commit, tag, and push.
# Usage: mise run release <version>   (e.g. mise run release 0.2.0)
set -euo pipefail

version="${1:?usage: mise run release <version> (e.g. 0.2.0)}"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo "invalid version: $version (expected X.Y.Z)"
    exit 1
}
[[ -z "$(git status --porcelain)" ]] || {
    echo "working tree is not clean; commit or stash changes first"
    exit 1
}
if git rev-parse "v$version" > /dev/null 2>&1; then
    echo "tag v$version already exists"
    exit 1
fi

# Rewrite only the version value so the oxfmt-formatted JSON stays untouched.
python - "$version" << 'EOF'
import re
import sys
from pathlib import Path

version = sys.argv[1]
manifests = {
    ".claude-plugin/plugin.json": (r'"version": "[^"]*"', f'"version": "{version}"'),
    ".codex-plugin/plugin.json": (r'"version": "[^"]*"', f'"version": "{version}"'),
    "agents/apm.yml": (r"(?m)^version: .*$", f"version: {version}"),
}
for manifest, (pattern, replacement) in manifests.items():
    path = Path(manifest)
    text, count = re.subn(pattern, replacement, path.read_text())
    if count != 1:
        sys.exit(f"{manifest}: expected exactly one version field, found {count}")
    path.write_text(text)
    print(f"{manifest}: version -> {version}")
EOF

git commit -am "chore: release v$version"
git tag "v$version"
git push origin HEAD "v$version"
echo "released v$version"
