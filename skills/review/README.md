# review

## skill-review

Score an agent skill (its `SKILL.md` and bundled files) against a fixed set of criteria and report, per criterion, a verdict with evidence and a suggested fix. The skill evaluates only; applying fixes waits for a separate request.

| Argument    | Effect                                                                                                                       |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `<path>`    | Skill directory or `SKILL.md` to evaluate. Several may be given. Without it, the repository is scanned and the user chooses. |
| `--propose` | Skip evaluation and only confirm criteria candidates noted earlier in the conversation.                                      |

Evaluation starts with a specification gate (Agent Skills frontmatter and structure), then eleven criteria: goal and boundaries, description quality, amount of command examples, completion criteria, early return, self-containment, conciseness, splitting into references, readability, freshness, and client compatibility. Each is judged pass, needs improvement, not applicable, or undetermined; "needs improvement" always quotes the offending lines. Freshness includes running `shellcheck`, `shfmt`, and `ruff` on bundled scripts and executing them with side-effect-free arguments.

The criteria live in `skill-review/references/criteria.md` with a change history in `references/CHANGELOG.md`. Before each run, `scripts/check_criteria.sh` compares the criteria against a recorded baseline and asks the user to log any change. After a review, decisions made while fixing skills can be promoted into new criteria through a single confirmation, which updates the criteria, the changelog, and the baseline together.

- Trigger phrases: "このskillを評価して", "skillをレビューして", "SKILL.mdの品質を見て".

The per-criterion rules and the report format live in `SKILL.md` and `references/criteria.md`.

## test-prune

Examine every test in the codebase and list the ones that can be deleted or merged. Targets are copies of the implementation, mocks verifying themselves, re-checks of what types or libraries already guarantee, duplicates of other tests, over-reliance on internals, and excessive case splitting. The criterion is "if this test were deleted, what realistic bug would go unnoticed?"; neither test count nor coverage is a goal.

- Trigger phrases: "テストを減らして", "不要なテストを洗い出して", "テストを整理して".
