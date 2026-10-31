# github-pr-review

[日本語](README_ja.md)

Adversarially review a GitHub Pull Request and post only verified findings as a review report plus inline comments. The review is shown for confirmation before posting; with `--auto` it is posted without asking. Two Finder subagents with different focuses and (when a spec is available) a Contract subagent propose findings from a snapshot worktree of the PR head. Every candidate is challenged by an independent Verifier subagent, and only confirmed findings are posted. Self review is supported.

The spec is resolved from `--spec` or from the issue in the PR's `Closes #N`, with comments from maintainers (owners, members, collaborators) appended after the issue body; when neither exists, the Contract axis is skipped. The skip is not posted to the PR; only the chat report mentions it. To grade your own changes without posting anything, use `self-review` instead.

## Usage

- "このPRをレビューして"

```text
/github-pr-review
/github-pr-review 123
/github-pr-review 123 --spec 45
/github-pr-review 123 --auto
```

## Arguments

| Argument         | Effect                                                                           |
| ---------------- | -------------------------------------------------------------------------------- |
| `PR number`      | PR to review. Defaults to the current branch's PR, or asks when there is none.   |
| `--spec <issue>` | Issue used as the spec for the Contract axis. Overrides the PR's `Closes` issue. |
| `--auto`         | Skip the confirmation before posting and post right away.                        |

## Behavior

- One PR per run. The PR head is checked out detached in a dedicated worktree, and all review reads that snapshot.
- `scripts/resolve_review_range.sh` decides the review range: from the merge-base with the base branch to the PR head. For a PR stacked on another unmerged open PR, only the commits after that PR's head are reviewed. Large inputs such as the diff reach subagents as files in the temp directory.
- Candidates are deduplicated by location or root cause, then each is verified one by one. `refuted` and `uncertain` verdicts are dropped. Findings are ordered Finder, Contract, and Contract drops a finding that duplicates an earlier one.
- If any subagent cannot start or returns nothing, the review stops without posting, dismissing, or resolving, and reports why. The skill does not review the diff itself as a substitute.
- Failed CI results are used as evidence for the Finders and noted in the report summary.
- Earlier findings on the same PR and their replies, including resolved threads, are fetched by `scripts/fetch_prior_findings.sh` and passed to subagents. A candidate with the same root cause as a finding that was settled as deferred or declined is dropped before verification unless it shows that the premise of that decision has changed, so settled findings are not raised again.
- The report language (`ja` or `en`) is decided by `scripts/render_review.py` from the PR title and body. The same script renders the review body and inline comments from a findings JSON (format in `references/findings.md`). The Verdict is `REQUEST_CHANGES` with one or more findings and `APPROVE` with none.
- Before posting, the Verdict, report body, inline comments, and the number of reviews to dismiss and threads to resolve are shown, and the user chooses to post, revise and show again, or cancel. `--auto` skips this confirmation.
- Posting goes through `scripts/post_review.sh`, which drops inline comments whose `(path, line, side)` is not in the diff. Body and comments are passed as files.
- Self review is posted as a `COMMENT` event, since GitHub does not allow approving or requesting changes on your own PR. The Verdict text in the body is unchanged.
- After a successful post, earlier reviews by the same reviewer are dismissed (`scripts/dismiss_my_reviews.sh`) and their threads are resolved (`scripts/resolve_review_threads.sh`). If posting fails, nothing is dismissed or resolved.
- If the PR head moves during the review, confirmed findings are posted as a `COMMENT` on the reviewed commit and earlier reviews are left as they are. With no findings, nothing is posted.
- The worktree, temporary refs, and temp directory are removed at the end, including after an interruption.
- Private repository information is not written into reviews posted to public repositories.

## Dependencies

- Agents: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md), [`code-reviewer-contract`](../../../agents/code-reviewer-contract.md), [`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md). They ship through the Claude Code plugin and apm; with `apm install -t codex` they are converted to Codex agent format and the `tools` restriction is dropped. On other install methods, generic subagents receive the same prompts.
- `git`, `gh`, `jq`, and Python

The full procedure lives in [SKILL.md](SKILL.md).
