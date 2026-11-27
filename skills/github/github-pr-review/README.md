# github-pr-review

[日本語](README_ja.md)

Adversarially review a GitHub Pull Request and post only verified findings as a review report plus inline comments. The review is shown for confirmation before posting; with `--auto` it is posted without asking. Working from a snapshot worktree of the PR head, two Finder subagents with different focuses propose findings and a Claim subagent checks the claims in the PR body against the real code. Every candidate is challenged by an independent Verifier subagent that runs the code. Findings it reproduces are posted as required changes, and findings it could neither reproduce nor refute are posted as unproven. Self review is supported.

To grade your own changes without posting anything, use `self-review` instead.

## Usage

- "このPRをレビューして"

```text
/github-pr-review
/github-pr-review 123
/github-pr-review 123 --auto
```

## Arguments

| Argument    | Effect                                                                         |
| ----------- | ------------------------------------------------------------------------------ |
| `PR number` | PR to review. Defaults to the current branch's PR, or asks when there is none. |
| `--auto`    | Skip the confirmation before posting and post right away.                      |

## Behavior

- One PR per run. The PR head is checked out detached in a dedicated worktree, and all review reads that snapshot.
- `scripts/resolve_review_range.sh` decides the review range: from the merge-base with the base branch to the PR head. For a PR stacked on another unmerged open PR, only the commits after that PR's head are reviewed. Large inputs such as the diff reach subagents as files in the temp directory.
- First it restates the intent of the change in two or three sentences from the PR title and body, commits, and diff, and passes it to the subagents. Findings are judged by whether that intent is broken.
- Finder, Claim, and Verifier may run tests and reproduction code. Each subagent runs them in its own copy exported from the snapshot to a temporary directory and never changes the snapshot. Finder attaches to each finding a reproduction that runs as is, with its output.
- Claim runs the validation, scope, and blast radius statements in the PR body and proposes the mismatches it observes. It does not decide whether the description or the code is right.
- Candidates are deduplicated by location or root cause, then each is verified one by one. Verifier reruns the reproduction itself. `refuted` and `uncertain` verdicts are dropped and only counted in the chat report. Confirmed findings that Verifier reproduced become required changes, and those it only traced through the code become unproven findings. Findings are ordered Finder, Claim, and Claim drops a finding that duplicates an earlier one.
- If any subagent cannot start or returns nothing, the review stops without posting, dismissing, or resolving, and reports why. The skill does not review the diff itself as a substitute.
- Failed CI results are used as evidence for the Finders and noted in the report summary.
- Earlier findings on the same PR and their replies, including resolved threads, are fetched by `scripts/fetch_prior_findings.sh` and passed to subagents. A candidate with the same root cause as a finding that was settled as deferred or declined is dropped before verification unless it shows that the premise of that decision has changed, so settled findings are not raised again.
- The report language (`ja` or `en`) is decided by `scripts/render_review.py` from the PR title and body. The same script renders the full report for the chat, the inline comments, and the review body posted to GitHub from a findings JSON (format in `references/findings.md`). The review body is a table of findings, and each row links to the inline comment that carries the details. The Verdict is `REQUEST_CHANGES` with one or more required changes and `APPROVE` with none. Unproven findings appear in the report and inline comments but do not change the Verdict. Each required change carries its reproduction and output.
- Before posting, the skill shows the Verdict, the full report, and the number of reviews to dismiss and threads to resolve. The user then chooses to post, revise and show again, or cancel. `--auto` skips this confirmation.
- Posting goes through `scripts/post_review.sh`. It creates the inline comments in a pending review first, then publishes the review with a body whose table links to them. If it fails before publishing, it deletes the pending review. A finding whose `(path, line, side)` is not in the diff cannot get an inline comment, so the review body carries its details.
- Self review is posted as a `COMMENT` event, since GitHub does not allow approving or requesting changes on your own PR. The Verdict text in the body is unchanged.
- After a successful post, earlier reviews by the same reviewer are dismissed (`scripts/dismiss_my_reviews.sh`) and their threads are resolved (`scripts/resolve_review_threads.sh`). If posting fails, nothing is dismissed or resolved.
- If the PR head moves during the review, confirmed findings are posted as a `COMMENT` on the reviewed commit and earlier reviews are left as they are. With no findings, nothing is posted.
- The worktree, temporary refs, and temp directory are removed at the end, including after an interruption.
- Private repository information is not written into reviews posted to public repositories.

## Dependencies

- Agents: [`code-reviewer-finder`](../../../agents/.apm/agents/code-reviewer-finder.md), [`code-reviewer-claim`](../../../agents/.apm/agents/code-reviewer-claim.md), [`code-reviewer-verifier`](../../../agents/.apm/agents/code-reviewer-verifier.md). They ship through the Claude Code plugin and apm; with `apm install -t codex` they are converted to Codex agent format and the `tools` restriction is dropped. On other install methods, generic subagents receive the same prompts.
- `git`, `gh`, `jq`, and Python

The full procedure lives in [SKILL.md](SKILL.md).
