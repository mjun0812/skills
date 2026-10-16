#!/usr/bin/env bash
# Resolve the commit range a PR review covers and write the review inputs.
#
# Usage:
#   resolve_review_range.sh \
#     --repo <owner/repo> \
#     --pr <number> \
#     --base-ref <fetched base branch ref> \
#     --head <head commit sha> \
#     --out-dir <dir>
#
# Behavior:
#   - The baseline starts at the merge-base of --base-ref and --head, so
#     commits added to the base branch after the PR branched never appear
#     in the diff.
#   - If the head of another open PR sits between that merge-base and
#     --head (a stacked PR whose dependency is not merged yet), the nearest
#     such head becomes the baseline and its changes are left to that PR.
#   - Writes <out-dir>/diff.patch, <out-dir>/changed-files.txt (name-status)
#     and <out-dir>/commits.txt (one commit per line) for that range.
#
# Prints a JSON object to stdout:
#   {"mergeBase": sha, "baseline": sha, "dependencyPr": number|null}

set -euo pipefail

REPO=""
PR=""
BASE_REF=""
HEAD=""
OUT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
    --repo)
        REPO="$2"
        shift 2
        ;;
    --pr)
        PR="$2"
        shift 2
        ;;
    --base-ref)
        BASE_REF="$2"
        shift 2
        ;;
    --head)
        HEAD="$2"
        shift 2
        ;;
    --out-dir)
        OUT_DIR="$2"
        shift 2
        ;;
    *)
        echo "Unknown argument: $1" >&2
        exit 2
        ;;
    esac
done

if [[ -z $REPO || -z $PR || -z $BASE_REF || -z $HEAD || -z $OUT_DIR ]]; then
    echo "Missing required argument: --repo, --pr, --base-ref, --head and --out-dir are required" >&2
    exit 2
fi

MERGE_BASE=$(git merge-base "$BASE_REF" "$HEAD")
BASELINE="$MERGE_BASE"
DEPENDENCY_PR="null"
BEST_COUNT=0

while IFS=$'\t' read -r number oid; do
    [[ $number == "$PR" || $oid == "$HEAD" ]] && continue
    # A dependency head reachable from this PR's head is already local.
    git cat-file -e "${oid}^{commit}" 2> /dev/null || continue
    git merge-base --is-ancestor "$oid" "$HEAD" || continue
    git merge-base --is-ancestor "$oid" "$BASE_REF" && continue
    count=$(git rev-list --count "${MERGE_BASE}..${oid}")
    if ((count > BEST_COUNT)); then
        BEST_COUNT=$count
        BASELINE="$oid"
        DEPENDENCY_PR="$number"
    fi
done < <(gh pr list --repo "$REPO" --state open --limit 200 \
    --json number,headRefOid --jq '.[] | [.number, .headRefOid] | @tsv')

mkdir -p "$OUT_DIR"
git diff --no-ext-diff "$BASELINE" "$HEAD" > "$OUT_DIR/diff.patch"
git diff --no-ext-diff --name-status "$BASELINE" "$HEAD" > "$OUT_DIR/changed-files.txt"
git log --format='%H %s' "${BASELINE}..${HEAD}" > "$OUT_DIR/commits.txt"

jq -n --arg mergeBase "$MERGE_BASE" --arg baseline "$BASELINE" \
    --argjson dependencyPr "$DEPENDENCY_PR" \
    '{mergeBase: $mergeBase, baseline: $baseline, dependencyPr: $dependencyPr}'
