#!/usr/bin/env bash
# Show a self-review's findings as notes in a live Hunk session.
#
# Reuses the Hunk session already open for the repository, or opens Hunk in a
# new Herdr pane when running inside Herdr. Notes left by a previous
# self-review are removed, the session is reloaded with the reviewed diff, and
# the notes are applied with the author self-review.
#
# Usage: self_review_hunk.sh show --metadata <metadata.json> --notes <notes.json>
#
# notes.json uses the `hunk session comment apply` shape:
#   {"comments": [{"filePath": "...", "newLine": 1, "summary": "...", "rationale": "..."}]}
# A note on a deleted line uses "oldLine" instead of "newLine".
#
# Prints {"sessionId", "paneId", "applied", "omitted"} to stdout.
# Exit status 3 means Hunk is unavailable here; the caller skips the display.

set -euo pipefail

usage() {
    echo "Usage: $0 show --metadata <metadata.json> --notes <notes.json>" >&2
    exit 2
}

[[ $# -eq 5 && $1 == "show" && $2 == "--metadata" && $4 == "--notes" ]] || usage
metadata_path="$3"
notes_path="$5"

command -v hunk > /dev/null || {
    echo "hunk is not installed." >&2
    exit 3
}

repo_root=$(jq -er '.repoRoot' "$metadata_path")
mode=$(jq -er '.mode' "$metadata_path")
if [[ $mode == "branch" ]]; then
    # Hunk compares the working tree, untracked files included, with the baseline.
    review_command=(diff "$(jq -er '.baselineSha' "$metadata_path")")
else
    review_command=(show "$(jq -er '.headSha' "$metadata_path")")
fi

# shellcheck disable=SC2016 # $repo is a jq variable.
session_query='[.sessions[]? | select(.repoRoot == $repo and .fileCount > 0)][0].sessionId // empty'
pane_id=""
session_id=$(hunk session list --json | jq -r --arg repo "$repo_root" "$session_query")
if [[ -n $session_id ]]; then
    # Remove the notes before the reload so that a failure, such as a user reply
    # to one of them, leaves the session as the user last saw it. `comment clear`
    # would also remove notes left by other agents.
    hunk session comment list "$session_id" --json |
        jq -r '.comments[] | select(.author == "self-review") | .commentId' |
        while IFS= read -r comment_id; do
            hunk session comment rm "$session_id" "$comment_id" > /dev/null
        done
    hunk session reload "$session_id" -- "${review_command[@]}" > /dev/null
elif [[ ${HERDR_ENV:-} == 1 ]] && command -v herdr > /dev/null; then
    read -r width height < <(herdr pane layout --pane "$HERDR_PANE_ID" |
        jq -r --arg pane "$HERDR_PANE_ID" \
            '.result.layout.panes[] | select(.pane_id == $pane) | "\(.rect.width) \(.rect.height)"')
    # Terminal cells are about twice as tall as wide.
    if ((width >= height * 2)); then
        direction="right"
    else
        direction="down"
    fi
    pane_id=$(herdr pane split --current --direction "$direction" --cwd "$repo_root" --no-focus |
        jq -er '.result.pane.pane_id')
    herdr pane run "$pane_id" "hunk ${review_command[*]}" > /dev/null
    for _ in $(seq 1 40); do
        session_id=$(hunk session list --json | jq -r --arg repo "$repo_root" "$session_query")
        [[ -n $session_id ]] && break
        sleep 0.5
    done
    [[ -n $session_id ]] || {
        echo "Hunk did not start in Herdr pane $pane_id." >&2
        exit 4
    }
else
    echo "No Hunk session is open for $repo_root, and this is not a Herdr pane." >&2
    exit 3
fi

# Hunk rejects the whole batch when one note is outside the diff, so keep only
# notes on lines that a hunk covers on their side.
review=$(hunk session review "$session_id" --json)
notes=$(jq --argjson review "$review" '
    [$review.review.files[] | {path, hunks}] as $files
    | {comments: [.comments[] | select(
        . as $note
        | any($files[]; .path == $note.filePath
            and any(.hunks[];
                if $note.oldLine != null then .oldRange else .newRange end as $range
                | ($note.oldLine // $note.newLine) as $line
                | $range[0] <= $line and $line <= $range[1])))
        | .author = "self-review"]}
    ' "$notes_path")
applied=$(jq '.comments | length' <<< "$notes")
omitted=$(($(jq '.comments | length' "$notes_path") - applied))

if ((applied > 0)); then
    hunk session comment apply "$session_id" --stdin --focus > /dev/null <<< "$notes"
fi

jq -n --arg sessionId "$session_id" --arg paneId "$pane_id" \
    --argjson applied "$applied" --argjson omitted "$omitted" \
    '{sessionId: $sessionId, paneId: $paneId, applied: $applied, omitted: $omitted}'
