# github

Skills for the GitHub side of a change: issues, pull requests, CI, and review. They all drive GitHub through the `gh` CLI, and the ones that write to a PR or issue detect the language from its title and body and reply in kind.

## Which skill to use

| Situation                                                                 | Skill                                                              |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| File one issue from a note, todo, or bug report                           | [`github-issue-create`](github-issue-create/README.md)             |
| Sharpen an existing issue until it can be implemented from the text alone | [`github-issue-polish`](github-issue-polish/README.md)             |
| Implement an issue end to end and open the PR                             | [`github-issue-resolve`](github-issue-resolve/README.md)           |
| Triage all open issues: close, comment, relabel in bulk                   | [`github-issue-update`](github-issue-update/README.md)             |
| Open a PR from the current branch                                         | [`github-pr-create`](github-pr-create/README.md)                   |
| Review a PR and post findings                                             | [`github-pr-review`](github-pr-review/README.md)                   |
| Act on review comments only, in the current working tree                  | [`github-resolve-pr-comment`](github-resolve-pr-comment/README.md) |
| Fix failing CI                                                            | [`github-fix-ci`](github-fix-ci/README.md)                         |
| Fix everything blocking a PR (conflicts, CI, review comments) in one go   | [`github-pr-fix`](github-pr-fix/README.md)                         |
| Report one user's PR, issue, review, and coding agent work for a period   | [`work-report`](work-report/README.md)                             |

`github-pr-fix` orchestrates `git-fix-conflict`, `github-fix-ci`, and `github-resolve-pr-comment`. It is the default for a request to handle review comments; go to `git-fix-conflict` or `github-fix-ci` directly when only conflicts or only CI need fixing. `github-issue-resolve` chains into `git-commit` and `github-pr-create` for the final steps.
