#!/usr/bin/env bash
# Resolve the base ref of the current branch's changes, its open PR, and the
# size of each review target the caller can propose.
#
# Without --base, the base is the open PR's base branch, or the default branch
# of the repository gh resolves when there is no PR. The branch is fetched from
# the local remote that points to that repository, so a fork's stale
# origin/main is never used as the base of an upstream PR.
#
# Usage: self_review_target.sh --repo <path> [--base <ref>]
#
# Prints to stdout:
#   {"base": "<ref>", "pr": {"number", "title", "body"} | null,
#    "commits": <commits since the merge-base>, "hasUncommitted": <bool>,
#    "untrackedFiles": <count>,
#    "stats": {"branch": "<shortstat>", "uncommitted": "<shortstat>", "head": "<shortstat>"}}
# The shortstats count tracked files only; untrackedFiles is reported apart.
# Exit status 10 means the base could not be resolved; pass --base.

set -euo pipefail

usage() {
    echo "Usage: $0 --repo <path> [--base <ref>]" >&2
    exit 2
}

[[ ($# -eq 2 || $# -eq 4) && $1 == "--repo" ]] || usage
repo_root=$(git -C "$2" rev-parse --show-toplevel)
base=""
if [[ $# -eq 4 ]]; then
    [[ $3 == "--base" ]] || usage
    base="$4"
fi
cd "$repo_root"

pr_json=$(gh pr view --json number,state,title,body,baseRefName,url 2> /dev/null || true)
if [[ -n $pr_json && $(jq -r '.state' <<< "$pr_json") == "OPEN" ]]; then
    pr=$(jq '{number, title, body}' <<< "$pr_json")
    base_repo=$(jq -r '.url' <<< "$pr_json" | sed -E 's#^https?://[^/]+/([^/]+/[^/]+)/pull/[0-9]+$#\1#')
    base_branch=$(jq -r '.baseRefName' <<< "$pr_json")
else
    pr="null"
    if [[ -z $base ]]; then
        if ! repo_json=$(gh repo view --json nameWithOwner,defaultBranchRef 2> /dev/null); then
            echo "Could not resolve the GitHub repository with gh. Pass --base." >&2
            exit 10
        fi
        base_repo=$(jq -r '.nameWithOwner' <<< "$repo_json")
        base_branch=$(jq -r '.defaultBranchRef.name' <<< "$repo_json")
    fi
fi

if [[ -z $base ]]; then
    base_remote=""
    while IFS= read -r remote; do
        remote_repo=$(git remote get-url "$remote" | sed -E 's#\.git$##; s#^.*[:/]([^/:]+/[^/:]+)$#\1#')
        if [[ $(tr '[:upper:]' '[:lower:]' <<< "$remote_repo") == $(tr '[:upper:]' '[:lower:]' <<< "$base_repo") ]]; then
            base_remote="$remote"
            break
        fi
    done < <(git remote)
    [[ -n $base_remote ]] || {
        echo "No git remote points to $base_repo. Pass --base." >&2
        exit 10
    }
    git fetch --quiet "$base_remote" "+refs/heads/$base_branch:refs/remotes/$base_remote/$base_branch"
    base="$base_remote/$base_branch"
fi

if ! base_sha=$(git rev-parse --verify --end-of-options "${base}^{commit}"); then
    echo "Base not found: $base" >&2
    exit 10
fi
if ! merge_base=$(git merge-base "$base_sha" HEAD); then
    echo "HEAD has no common ancestor with the base: $base" >&2
    exit 10
fi
untracked_files=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')
if git diff --quiet HEAD -- && ((untracked_files == 0)); then
    has_uncommitted=false
else
    has_uncommitted=true
fi

jq -n --arg base "$base" --argjson pr "$pr" \
    --argjson commits "$(git rev-list --count "${merge_base}..HEAD")" \
    --argjson hasUncommitted "$has_uncommitted" \
    --argjson untrackedFiles "$untracked_files" \
    --arg branch "$(git diff --shortstat "$merge_base" --)" \
    --arg uncommitted "$(git diff --shortstat HEAD --)" \
    --arg head "$(git show --shortstat --format= HEAD --)" \
    '{base: $base, pr: $pr, commits: $commits, hasUncommitted: $hasUncommitted,
      untrackedFiles: $untrackedFiles,
      stats: {branch: $branch, uncommitted: $uncommitted, head: $head} | map_values(ltrimstr(" "))}'
