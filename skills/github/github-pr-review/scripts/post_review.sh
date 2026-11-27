#!/usr/bin/env bash
# Post a new PR review via GitHub API. Each finding's details go into an inline
# comment, and the review body lists the findings in tables that link to them.
#
# Usage:
#   post_review.sh \
#     --repo <owner/repo> \
#     --pr <number> \
#     --commit <sha> \
#     --event <APPROVE|REQUEST_CHANGES|COMMENT> \
#     --pr-text <path-to-pr.md> \
#     --findings <path-to-findings.json> \
#     --out-dir <dir>
#
# Pass the same --pr-text, --findings, and --out-dir that render_review.py was
# run with. <dir> must hold the comments.json it wrote; this script writes
# posted.json and body.md there.
#
# To dismiss existing reviews, use scripts/dismiss_my_reviews.sh separately.
# To resolve threads replaced by this review, use scripts/resolve_review_threads.sh.
#
# - The inline comments are created in a pending review first, so their URLs
#   exist when the body is rendered. Submitting the pending review with that
#   body publishes the body and the comments at once.
# - A finding whose (path, line, side) is not part of the PR diff cannot get an
#   inline comment. The review body carries its details instead.
# - A user can hold only one pending review per PR, so the pending review is
#   deleted when anything fails before it is submitted.
#
# On success, prints the review's HTML URL to stdout.

set -euo pipefail

REPO=""
PR=""
COMMIT=""
EVENT=""
PR_TEXT=""
FINDINGS=""
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
    --commit)
        COMMIT="$2"
        shift 2
        ;;
    --event)
        EVENT="$2"
        shift 2
        ;;
    --pr-text)
        PR_TEXT="$2"
        shift 2
        ;;
    --findings)
        FINDINGS="$2"
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

require() {
    local value="$1" flag="$2"
    if [[ -z $value ]]; then
        echo "Missing required argument: $flag" >&2
        exit 2
    fi
}
require "$REPO" --repo
require "$PR" --pr
require "$COMMIT" --commit
require "$EVENT" --event
require "$PR_TEXT" --pr-text
require "$FINDINGS" --findings
require "$OUT_DIR" --out-dir

case "$EVENT" in
APPROVE | REQUEST_CHANGES | COMMENT) ;;
*)
    echo "--event must be APPROVE, REQUEST_CHANGES, or COMMENT (got: $EVENT)" >&2
    exit 2
    ;;
esac

COMMENTS_FILE="${OUT_DIR}/comments.json"
POSTED_FILE="${OUT_DIR}/posted.json"
BODY_FILE="${OUT_DIR}/body.md"

for file in "$PR_TEXT" "$FINDINGS" "$COMMENTS_FILE"; do
    if [[ ! -f $file ]]; then
        echo "File not found: $file" >&2
        exit 2
    fi
done

PAYLOAD_FILE=$(mktemp)
PR_FILES_FILE=$(mktemp)
VALID_COMMENTS_FILE=$(mktemp)
PENDING_REVIEW_ID=""
trap 'rm -f "$PAYLOAD_FILE" "$PR_FILES_FILE" "$VALID_COMMENTS_FILE"; [[ -z $PENDING_REVIEW_ID ]] || gh api -X DELETE "repos/${REPO}/pulls/${PR}/reviews/${PENDING_REVIEW_ID}" > /dev/null' EXIT

# Keep only the comments whose (path, line, side) is part of the PR diff;
# the others cannot be posted inline.
gh api "repos/${REPO}/pulls/${PR}/files?per_page=100" --paginate --jq '.[]' | jq -s '.' > "$PR_FILES_FILE"

jq --slurpfile comments "$COMMENTS_FILE" '
    def parse_patch:
      if . == null or . == "" then []
      else
        split("\n")
        | reduce .[] as $l (
            {old: 0, new: 0, lines: []};
            if ($l | test("^@@ -[0-9]+")) then
              ($l | capture("@@ -(?<os>[0-9]+)(,[0-9]+)? \\+(?<ns>[0-9]+)(,[0-9]+)? @@")) as $h
              | .old = ($h.os | tonumber)
              | .new = ($h.ns | tonumber)
            elif ($l | startswith("+++")) or ($l | startswith("---")) or ($l | startswith("\\")) then
              .
            elif ($l | startswith("+")) then
              .lines += [{line: .new, side: "RIGHT"}]
              | .new += 1
            elif ($l | startswith("-")) then
              .lines += [{line: .old, side: "LEFT"}]
              | .old += 1
            else
              .lines += [{line: .new, side: "RIGHT"}, {line: .old, side: "LEFT"}]
              | .new += 1
              | .old += 1
            end
          )
        | .lines
      end;

    (
      [ .[] | (.patch // "") as $p | .filename as $f | ($p | parse_patch) | map(. + {path: $f}) ]
      | flatten
      | map("\(.path):\(.line):\(.side)")
      | unique
    ) as $valid_set
    | [ $comments[0][] | select(("\(.path):\(.line):\(.side // "RIGHT")") as $key | $valid_set | index($key) != null) ]
  ' "$PR_FILES_FILE" > "$VALID_COMMENTS_FILE"

VALID_COUNT=$(jq 'length' "$VALID_COMMENTS_FILE")
INVALID_COUNT=$(($(jq 'length' "$COMMENTS_FILE") - VALID_COUNT))

if [[ $INVALID_COUNT -gt 0 ]]; then
    echo "Warning: ${INVALID_COUNT} finding(s) target lines not in the PR diff; the review body carries their details instead of an inline comment." >&2
fi

if [[ $VALID_COUNT -gt 0 ]]; then
    # No event: the review stays pending and invisible until it is submitted.
    jq -n \
        --arg commit_id "$COMMIT" \
        --slurpfile comments "$VALID_COMMENTS_FILE" \
        '{commit_id: $commit_id, comments: $comments[0]}' \
        > "$PAYLOAD_FILE"
    PENDING_REVIEW_ID=$(gh api -X POST "repos/${REPO}/pulls/${PR}/reviews" --input "$PAYLOAD_FILE" --jq '.id')
    gh api "repos/${REPO}/pulls/${PR}/reviews/${PENDING_REVIEW_ID}/comments?per_page=100" --paginate --jq '.[]' | jq -s '.' > "$POSTED_FILE"
else
    echo '[]' > "$POSTED_FILE"
fi

python "$(dirname "$0")/render_review.py" \
    --pr-text "$PR_TEXT" \
    --findings "$FINDINGS" \
    --out-dir "$OUT_DIR" \
    --posted "$POSTED_FILE" \
    > /dev/null

if [[ -n $PENDING_REVIEW_ID ]]; then
    jq -n \
        --rawfile body "$BODY_FILE" \
        --arg event "$EVENT" \
        '{body: $body, event: $event}' \
        > "$PAYLOAD_FILE"
    gh api -X POST "repos/${REPO}/pulls/${PR}/reviews/${PENDING_REVIEW_ID}/events" --input "$PAYLOAD_FILE" --jq '.html_url'
    PENDING_REVIEW_ID=""
else
    jq -n \
        --rawfile body "$BODY_FILE" \
        --arg commit_id "$COMMIT" \
        --arg event "$EVENT" \
        '{body: $body, commit_id: $commit_id, event: $event}' \
        > "$PAYLOAD_FILE"
    gh api -X POST "repos/${REPO}/pulls/${PR}/reviews" --input "$PAYLOAD_FILE" --jq '.html_url'
fi
