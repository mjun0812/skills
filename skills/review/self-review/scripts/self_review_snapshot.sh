#!/usr/bin/env bash
# Pin local changes into a detached review worktree, then verify or remove it.
#
# create-branch reviews everything since the merge-base with --base: the
# branch's commits plus staged, unstaged and untracked changes.
#
# Usage: self_review_snapshot.sh create-branch --repo <path> --base <ref>
#        self_review_snapshot.sh create-commit --repo <path> --commit <commit>
#        self_review_snapshot.sh verify --metadata <metadata.json>
#        self_review_snapshot.sh cleanup --metadata <metadata.json>

set -euo pipefail

usage() {
    echo "Usage: $0 create-branch --repo <path> --base <ref>" >&2
    echo "       $0 create-commit --repo <path> --commit <commit>" >&2
    echo "       $0 verify --metadata <metadata.json>" >&2
    echo "       $0 cleanup --metadata <metadata.json>" >&2
    exit 2
}

write_state_manifest() {
    local repo_root="$1"
    local output_path="$2"
    local relative_path
    local file_type

    # HEAD is part of the state so that a new commit invalidates the snapshot.
    printf 'HEAD %s\n' "$(git -C "$repo_root" rev-parse --verify HEAD)" > "$output_path"
    git -C "$repo_root" diff --binary --full-index HEAD -- >> "$output_path"
    git -C "$repo_root" ls-files --others --exclude-standard -z |
        while IFS= read -r -d '' relative_path; do
            if [[ -L "$repo_root/$relative_path" ]]; then
                file_type="symlink"
            elif [[ -x "$repo_root/$relative_path" ]]; then
                file_type="executable"
            else
                file_type="file"
            fi
            printf '\0untracked\0%s\0%s\0' "$relative_path" "$file_type"
            git -C "$repo_root" hash-object --no-filters -- "$relative_path"
        done >> "$output_path"
}

metadata_value() {
    local metadata_path="$1"
    local query="$2"

    jq -er "$query" "$metadata_path"
}

# Resolve the metadata file to an absolute, symlink-free path.
resolve_metadata_path() {
    local metadata_path="$1"

    printf '%s/%s\n' "$(cd "$(dirname "$metadata_path")" && pwd -P)" "$(basename "$metadata_path")"
}

command_name="${1:-}"
[[ -n $command_name ]] || usage
shift

case "$command_name" in
create-branch | create-commit)
    if [[ $command_name == "create-branch" ]]; then
        [[ $# -eq 4 && $1 == "--repo" && $3 == "--base" ]] || usage
        repo_arg="$2"
        base_arg="$4"
        mode="branch"
    else
        [[ $# -eq 4 && $1 == "--repo" && $3 == "--commit" ]] || usage
        repo_arg="$2"
        commit_arg="$4"
        mode="commit"
    fi

    repo_root=$(git -C "$repo_arg" rev-parse --show-toplevel)
    if [[ $mode == "branch" ]]; then
        head_sha=$(git -C "$repo_root" rev-parse --verify HEAD)
        if ! base_sha=$(git -C "$repo_root" rev-parse --verify --end-of-options "${base_arg}^{commit}"); then
            echo "Base not found: $base_arg" >&2
            exit 10
        fi
        if ! baseline_sha=$(git -C "$repo_root" merge-base "$base_sha" "$head_sha"); then
            echo "HEAD has no common ancestor with the base: $base_arg" >&2
            exit 10
        fi
        untracked_count=$(git -C "$repo_root" ls-files --others --exclude-standard -z | wc -c | tr -d ' ')
        if git -C "$repo_root" diff --quiet HEAD -- && ((untracked_count == 0)); then
            has_uncommitted=false
        else
            has_uncommitted=true
        fi
        if [[ $has_uncommitted == false ]] && git -C "$repo_root" diff --quiet "$baseline_sha" "$head_sha" --; then
            echo "No changes to review since the merge-base with $base_arg." >&2
            exit 3
        fi
    else
        if ! snapshot_id=$(git -C "$repo_root" rev-parse --verify --end-of-options "${commit_arg}^{commit}"); then
            echo "Commit not found: $commit_arg" >&2
            exit 10
        fi
        if ! baseline_sha=$(git -C "$repo_root" rev-parse --verify "${snapshot_id}^1"); then
            echo "Root commits are not supported: $snapshot_id" >&2
            exit 10
        fi
        if git -C "$repo_root" diff --quiet "$baseline_sha" "$snapshot_id" --; then
            echo "The commit has no changes to review: $snapshot_id" >&2
            exit 3
        fi
        base_arg=""
        head_sha="$snapshot_id"
        has_uncommitted=false
    fi

    snapshot_root=$(mktemp -d /tmp/self-review.XXXXXX)
    snapshot_root=$(cd "$snapshot_root" && pwd -P)
    worktree_path="$snapshot_root/worktree"
    metadata_path="$snapshot_root/metadata.json"
    diff_path="$snapshot_root/diff.patch"
    changed_files_path="$snapshot_root/changed-files.txt"
    commits_path="$snapshot_root/commits.txt"
    tracked_patch="$snapshot_root/tracked.patch"
    state_before="$snapshot_root/state.before"
    state_after="$snapshot_root/state.after"
    worktree_state="$snapshot_root/worktree.state"

    if [[ "$snapshot_root/" == "$repo_root/"* ]]; then
        echo "Snapshot directory must be outside the repository." >&2
        rm -rf "$snapshot_root"
        exit 4
    fi

    # shellcheck disable=SC2154 # exit_code is assigned inside the trap body.
    trap '
            exit_code=$?
            if ((exit_code != 0)); then
                if [[ -n "${worktree_path:-}" && -d "$worktree_path" ]]; then
                    git -C "$repo_root" worktree remove --force "$worktree_path" >/dev/null 2>&1 || true
                fi
                if [[ -n "${snapshot_root:-}" && "${snapshot_root##*/}" == self-review.* ]]; then
                    rm -rf "$snapshot_root"
                fi
            fi
        ' EXIT

    if [[ $mode == "branch" ]]; then
        write_state_manifest "$repo_root" "$state_before"
        snapshot_id=$(git -C "$repo_root" hash-object "$state_before")
        git -C "$repo_root" diff --binary --full-index HEAD -- > "$tracked_patch"

        git -C "$repo_root" worktree add --detach "$worktree_path" "$head_sha" > /dev/null
        if [[ -s $tracked_patch ]]; then
            git -C "$worktree_path" apply --binary --whitespace=nowarn "$tracked_patch"
        fi

        git -C "$repo_root" ls-files --others --exclude-standard -z |
            while IFS= read -r -d '' relative_path; do
                destination="$worktree_path/$relative_path"
                mkdir -p "$(dirname "$destination")"
                cp -a "$repo_root/$relative_path" "$destination"
            done

        git -C "$worktree_path" add -A
        git -C "$worktree_path" diff --cached --binary --full-index "$baseline_sha" -- > "$diff_path"
        git -C "$worktree_path" diff --cached --name-status "$baseline_sha" -- > "$changed_files_path"
        git -C "$repo_root" log --format='%H %s' "${baseline_sha}..${head_sha}" > "$commits_path"

        write_state_manifest "$repo_root" "$state_after"
        current_snapshot_id=$(git -C "$repo_root" hash-object "$state_after")
        if [[ $current_snapshot_id != "$snapshot_id" ]]; then
            echo "The working tree changed while the snapshot was being created." >&2
            exit 5
        fi
        worktree_head="$head_sha"
    else
        git -C "$repo_root" worktree add --detach "$worktree_path" "$snapshot_id" > /dev/null
        git -C "$worktree_path" diff --binary --full-index "$baseline_sha" "$snapshot_id" -- > "$diff_path"
        git -C "$worktree_path" diff --name-status "$baseline_sha" "$snapshot_id" -- > "$changed_files_path"
        git -C "$repo_root" log -1 --format='%H %s' "$snapshot_id" > "$commits_path"
        worktree_head="$snapshot_id"
    fi

    write_state_manifest "$worktree_path" "$worktree_state"
    worktree_state_id=$(git -C "$worktree_path" hash-object "$worktree_state")

    jq -n \
        --arg mode "$mode" \
        --arg baseRef "$base_arg" \
        --argjson hasUncommitted "$has_uncommitted" \
        --arg repoRoot "$repo_root" \
        --arg worktree "$worktree_path" \
        --arg worktreeHead "$worktree_head" \
        --arg worktreeStateId "$worktree_state_id" \
        --arg baselineSha "$baseline_sha" \
        --arg headSha "$head_sha" \
        --arg snapshotId "$snapshot_id" \
        --arg diffFile "$diff_path" \
        --arg changedFilesFile "$changed_files_path" \
        --arg commitsFile "$commits_path" \
        '{
                version: 3,
                mode: $mode,
                baseRef: $baseRef,
                hasUncommitted: $hasUncommitted,
                repoRoot: $repoRoot,
                worktree: $worktree,
                worktreeHead: $worktreeHead,
                worktreeStateId: $worktreeStateId,
                baselineSha: $baselineSha,
                headSha: $headSha,
                snapshotId: $snapshotId,
                diffFile: $diffFile,
                changedFilesFile: $changedFilesFile,
                commitsFile: $commitsFile
            }' > "$metadata_path"

    rm -f "$tracked_patch" "$state_before" "$state_after" "$worktree_state"
    trap - EXIT
    printf '%s\n' "$metadata_path"
    ;;
verify)
    [[ $# -eq 2 && $1 == "--metadata" ]] || usage
    metadata_path="$2"
    [[ -f $metadata_path ]] || {
        echo "Snapshot metadata not found: $metadata_path" >&2
        exit 6
    }

    metadata_path=$(resolve_metadata_path "$metadata_path")
    snapshot_root=$(dirname "$metadata_path")
    [[ $snapshot_root == /tmp/self-review.* || $snapshot_root == /private/tmp/self-review.* ]] || {
        echo "Unexpected snapshot directory: $snapshot_root" >&2
        exit 9
    }

    version=$(metadata_value "$metadata_path" '.version')
    mode=$(metadata_value "$metadata_path" '.mode')
    repo_root=$(metadata_value "$metadata_path" '.repoRoot')
    worktree_path=$(metadata_value "$metadata_path" '.worktree')
    worktree_head=$(metadata_value "$metadata_path" '.worktreeHead')
    worktree_state_id=$(metadata_value "$metadata_path" '.worktreeStateId')
    head_sha=$(metadata_value "$metadata_path" '.headSha')
    snapshot_id=$(metadata_value "$metadata_path" '.snapshotId')

    [[ $version == "3" && ($mode == "branch" || $mode == "commit") ]] || {
        echo "Unsupported snapshot metadata." >&2
        exit 6
    }
    [[ $worktree_path == "$snapshot_root/worktree" && -d $worktree_path ]] || {
        echo "Review worktree is missing or invalid." >&2
        exit 9
    }

    current_worktree_head=$(git -C "$worktree_path" rev-parse --verify HEAD)
    if [[ $current_worktree_head != "$worktree_head" ]]; then
        echo "The review worktree HEAD changed after the snapshot was created." >&2
        exit 11
    fi

    state_file=$(mktemp /tmp/self-review-state.XXXXXX)
    trap 'rm -f "$state_file"' EXIT
    write_state_manifest "$worktree_path" "$state_file"
    current_worktree_state_id=$(git -C "$worktree_path" hash-object "$state_file")
    if [[ $current_worktree_state_id != "$worktree_state_id" ]]; then
        echo "The review worktree changed after the snapshot was created." >&2
        exit 11
    fi

    if [[ $mode == "branch" ]]; then
        current_head_sha=$(git -C "$repo_root" rev-parse --verify HEAD)
        if [[ $current_head_sha != "$head_sha" ]]; then
            echo "HEAD changed after the snapshot was created." >&2
            exit 7
        fi

        write_state_manifest "$repo_root" "$state_file"
        current_snapshot_id=$(git -C "$repo_root" hash-object "$state_file")
        if [[ $current_snapshot_id != "$snapshot_id" ]]; then
            echo "The working tree changed after the snapshot was created." >&2
            exit 8
        fi
    fi

    rm -f "$state_file"
    trap - EXIT
    printf '%s\n' "$snapshot_id"
    ;;
cleanup)
    [[ $# -eq 2 && $1 == "--metadata" ]] || usage
    metadata_path="$2"
    [[ -f $metadata_path ]] || {
        echo "Snapshot metadata not found: $metadata_path" >&2
        exit 6
    }

    metadata_path=$(resolve_metadata_path "$metadata_path")
    snapshot_root=$(dirname "$metadata_path")
    repo_root=$(metadata_value "$metadata_path" '.repoRoot')
    worktree_path=$(metadata_value "$metadata_path" '.worktree')

    [[ $snapshot_root == /tmp/self-review.* || $snapshot_root == /private/tmp/self-review.* ]] || {
        echo "Refusing to remove an unexpected snapshot directory: $snapshot_root" >&2
        exit 9
    }
    [[ $worktree_path == "$snapshot_root/worktree" ]] || {
        echo "Snapshot metadata contains an unexpected worktree path." >&2
        exit 9
    }
    [[ $snapshot_root != "/" && $snapshot_root != "$repo_root" ]] || {
        echo "Refusing to remove an unsafe snapshot directory." >&2
        exit 9
    }

    if [[ -d $worktree_path ]]; then
        git -C "$repo_root" worktree remove --force "$worktree_path" > /dev/null
    fi
    rm -rf "$snapshot_root"
    ;;
*)
    usage
    ;;
esac
