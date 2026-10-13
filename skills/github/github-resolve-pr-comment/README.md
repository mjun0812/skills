# github-resolve-pr-comment

[日本語](README_ja.md)

Collect the review comments on a PR, decide how to handle each, fix the code, and reply. It covers all three kinds of comments: inline review threads, review summary bodies, and PR-level issue comments. Each comment is classified as Must Fix, Should Fix, question, or information. Fixes are committed and pushed, every unresolved thread gets a reply, and one summary comment is posted at PR level.

To fix everything blocking a PR (conflicts, CI, and comments) in one run, use [`github-pr-fix`](../github-pr-fix/README.md), which calls this skill.

## Usage

- "レビューコメントに対応して"
- "PRコメントに返信して"

```text
/github-resolve-pr-comment
/github-resolve-pr-comment 123 --dry-run
```

## Arguments

| Argument    | Effect                                                                            |
| ----------- | --------------------------------------------------------------------------------- |
| `PR number` | PR to handle. Defaults to the current branch's PR.                                |
| `--dry-run` | Show the classification and planned response. No edits, commit, push, or replies. |

## Behavior

- Unresolved threads (`isResolved=false`) are the unit of work, regardless of review state or `isOutdated`. Resolved threads are skipped.
- Duplicate topics are merged with the inline thread preferred; comments the same reviewer explicitly retracted are dropped.
- Must Fix items are fixed, or answered with a technical reason if they cannot be. Should Fix items are adopted or declined with a stated reason. Questions are answered, and information is acknowledged when needed.
- Code changes are committed and pushed with a message in the PR's language (detected from its title and body, English when ambiguous). With no code change, commit and push are skipped.
- Replies to inline threads go to the thread's root comment through `scripts/post_review_reply.sh`. The PR-level summary goes through `scripts/post_issue_comment.sh`, using `references/comment_summary_template.md` or `_ja`. Bodies are always passed as files.
- The summary is written objectively, without conversational phrasing, and is printed as the final output.
- It asks the user before acting when a comment's intent is unclear or a large design change is needed.

## Dependencies

- `git` and `gh` CLI

The full procedure lives in [SKILL.md](SKILL.md).
