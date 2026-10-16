# self-review

[日本語](README_ja.md)

Adversarially review your own local changes (uncommitted changes, or one specified commit) and return only verified findings to the chat. The changes are pinned as a snapshot in a temporary worktree, and two Finder subagents with different focuses and (when a spec is given) a Contract subagent propose findings. Every candidate is challenged by an independent Verifier subagent, and only confirmed findings are reported.

It does not use GitHub, PRs, CI, or review threads. To review changes that are already in a PR and post the review, use `github-pr-review` instead.

## Usage

- "自分の変更を厳しくレビューして"
- "このcommitをself reviewして"

```text
/self-review
/self-review HEAD~1
/self-review --spec 45
/self-review --spec docs/specs/login/spec.md
```

## Arguments

| Argument          | Effect                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| `commit`          | Commit to review. Defaults to uncommitted changes (staged, unstaged, and untracked files not ignored).  |
| `--spec <source>` | Spec for the Contract axis: a GitHub issue number, or the path to a Markdown file holding the contract. |

## Behavior

- With a commit, only the diff between that commit and its first parent is reviewed. Root commits, whole-branch diffs, and GitHub PRs are out of scope.
- `scripts/self_review_snapshot.sh` creates the snapshot worktree under `/tmp/self-review.*`. The review reads only this snapshot and never changes your working tree.
- Finder only searches and reads the snapshot and runs no commands. Verifier may run the smallest relevant tests or reproduction code inside the snapshot.
- Candidates at the same location or with the same root cause are merged, then verified one by one. `refuted` and `uncertain` candidates are discarded. Findings are confirmed in the order Finder, Contract, and Contract drops candidates that duplicate an already confirmed finding.
- If a subagent cannot start or returns no result, the review stops and reports the cause. It never falls back to reading the diff itself.
- Before reporting, it checks that no agent changed the snapshot and, for uncommitted changes, that the original working tree is unchanged since the snapshot was created. If either changed, the results are discarded and only the need for a re-review is reported.
- The verdict is `CHANGES_REQUIRED` with one or more confirmed findings and `PASS` with none. Results go to the chat; nothing is saved to a file or posted to GitHub.
- The snapshot is removed at the end, including on interruption. The original repository is never reset, restored, stashed, checked out, or cleaned.

## Dependencies

- Agents: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md), [`code-reviewer-contract`](../../../agents/code-reviewer-contract.md), [`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md). They ship through the Claude Code plugin and apm. `apm install -t codex` converts them to Codex agent format, dropping the `tools` restriction. On other install methods, the same prompts are given to generic subagents instead.
- `git`, `jq`, bash, and `gh` when `--spec` is an issue number

See [SKILL.md](SKILL.md) for the full procedure.
