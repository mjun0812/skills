#!/usr/bin/env bash
# Show a self-review's findings as notes in a live Hunk session.
#
# Reuses the Hunk session already open for the repository, or opens Hunk in a
# new Herdr pane when running inside Herdr. Notes left by a previous
# self-review are removed, except those someone replied to, the session is
# reloaded with the reviewed diff, and the notes are applied with the author
# self-review.
#
# Usage: self_review_hunk.sh show --metadata <metadata.json> --notes <notes.json>
#
# notes.json uses the `hunk session comment apply` shape:
#   {"comments": [{"filePath": "...", "newLine": 1, "summary": "...", "rationale": "..."}]}
# A note on a deleted line uses "oldLine" instead of "newLine".
#
# Prints {"sessionId", "paneId", "applied", "omitted", "kept"} to stdout. kept
# counts previous self-review notes left in place because they have replies.
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

pane_id=""
kept=0
session_id=$(hunk session list --json |
    jq -r --arg repo "$repo_root" '[.sessions[]? | select(.repoRoot == $repo)][0].sessionId // empty')
if [[ -n $session_id ]]; then
    # Hunk refuses to remove a note with replies, and the replies hold the
    # user's discussion, so keep those notes. `comment clear` would also remove
    # notes left by other agents. `--type all` includes notes written in the TUI.
    previous_notes=$(hunk session comment list "$session_id" --type all --json)
    kept=$(jq '[.comments[].parentId // empty] as $parents
        | [.comments[] | select(.author == "self-review" and (.noteId as $id | $parents | index($id)))]
        | length' <<< "$previous_notes")
    jq -r '[.comments[].parentId // empty] as $parents
        | .comments[] | select(.author == "self-review" and (.noteId as $id | $parents | index($id) | not))
        | .noteId' <<< "$previous_notes" |
        while IFS= read -r note_id; do
            hunk session comment rm "$session_id" "$note_id" > /dev/null
        done
    hunk session reload "$session_id" -- "${review_command[@]}" > /dev/null
elif (($(jq '.comments | length' "$notes_path") == 0)); then
    # No previous notes to remove and nothing to show, so do not open a pane.
    echo "No Hunk session is open for $repo_root, and there are no notes to show." >&2
    exit 3
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
    # The session registers before Hunk has loaded the diff, so wait for files.
    for _ in $(seq 1 40); do
        session_id=$(hunk session list --json |
            jq -r --arg repo "$repo_root" \
                '[.sessions[]? | select(.repoRoot == $repo and .fileCount > 0)][0].sessionId // empty')
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
# notes on lines that a hunk covers on their side. Hunk identifies a renamed
# file by its new path, so an old-side note may name the previous path.
review=$(hunk session review "$session_id" --json)
notes=$(jq --argjson review "$review" '
    {comments: [.comments[] as $note
        | first($review.review.files[]
            | select(.path == $note.filePath
                or ($note.oldLine != null and .previousPath == $note.filePath))) as $file
        | select(any($file.hunks[];
            (if $note.oldLine != null then .oldRange else .newRange end) as $range
            | ($note.oldLine // $note.newLine) as $line
            | $range[0] <= $line and $line <= $range[1]))
        | $note | .filePath = $file.path | .author = "self-review"]}
    ' "$notes_path")
applied=$(jq '.comments | length' <<< "$notes")
omitted=$(($(jq '.comments | length' "$notes_path") - applied))

if ((applied > 0)); then
    hunk session comment apply "$session_id" --stdin --focus > /dev/null <<< "$notes"
fi

jq -n --arg sessionId "$session_id" --arg paneId "$pane_id" \
    --argjson applied "$applied" --argjson omitted "$omitted" --argjson kept "$kept" \
    '{sessionId: $sessionId, paneId: $paneId, applied: $applied, omitted: $omitted, kept: $kept}'
