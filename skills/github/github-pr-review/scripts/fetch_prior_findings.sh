#!/usr/bin/env bash
# Fetch every review thread the authenticated user started on a PR, resolved or not,
# together with the replies that record how each finding was handled.
#
# Usage:
#   fetch_prior_findings.sh --repo <owner/repo> --pr <number>
#
# Output: JSON array, oldest thread first:
#   [{"thread_id", "is_resolved", "path", "line", "created_at", "finding",
#     "replies": [{"author", "created_at", "body"}]}]

set -euo pipefail

REPO=""
PR=""

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
    *)
        echo "Unknown argument: $1" >&2
        exit 2
        ;;
    esac
done

if [[ -z $REPO || -z $PR ]]; then
    echo "Missing required argument: --repo and --pr are required" >&2
    exit 2
fi

OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
VIEWER="$(gh api user --jq .login)"
RESULT_FILE="$(mktemp)"
trap 'rm -f "$RESULT_FILE" "$RESULT_FILE.new"' EXIT

echo "[]" > "$RESULT_FILE"

CURSOR="null"
while :; do
    # shellcheck disable=SC2016  # the GraphQL query must not expand shell variables
    PAGE_JSON="$(gh api graphql \
        -F owner="$OWNER" \
        -F name="$NAME" \
        -F pr="$PR" \
        -F cursor="$CURSOR" \
        -f query='
      query($owner: String!, $name: String!, $pr: Int!, $cursor: String) {
        repository(owner: $owner, name: $name) {
          pullRequest(number: $pr) {
            reviewThreads(first: 50, after: $cursor) {
              pageInfo { hasNextPage endCursor }
              nodes {
                id
                isResolved
                path
                originalLine
                comments(first: 50) {
                  nodes { author { login } body createdAt }
                }
              }
            }
          }
        }
      }
    ')"

    PAGE_THREADS="$(echo "$PAGE_JSON" | jq --arg viewer "$VIEWER" '
    .data.repository.pullRequest.reviewThreads.nodes
    | map(select(.comments.nodes[0].author.login == $viewer))
    | map({
        thread_id: .id,
        is_resolved: .isResolved,
        path: .path,
        line: .originalLine,
        created_at: .comments.nodes[0].createdAt,
        finding: .comments.nodes[0].body,
        replies: [ .comments.nodes[1:][] | {
          author: (.author.login // "ghost"),
          created_at: .createdAt,
          body: .body
        } ]
      })
  ')"

    jq --argjson page "$PAGE_THREADS" '. + $page' "$RESULT_FILE" > "$RESULT_FILE.new"
    mv "$RESULT_FILE.new" "$RESULT_FILE"

    HAS_NEXT="$(echo "$PAGE_JSON" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')"
    END_CURSOR="$(echo "$PAGE_JSON" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor')"

    if [[ $HAS_NEXT != "true" ]]; then
        break
    fi

    CURSOR="$END_CURSOR"
done

jq 'sort_by(.created_at)' "$RESULT_FILE"
