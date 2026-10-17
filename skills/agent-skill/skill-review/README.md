# skill-review

[日本語](README_ja.md)

Score an agent skill (its `SKILL.md` and bundled files) against a fixed set of criteria and report, per criterion, a verdict with evidence and a suggested fix. The skill only evaluates; applying fixes waits for a separate request.

To create or edit a skill and check that agents actually follow it, use [`writing-skills`](../writing-skills/README.md) instead.

## Usage

- 「このskillを評価して」
- 「skillをレビューして」
- 「SKILL.mdの品質を見て」
- 「この判断を基準にして」 (promote a decision made while fixing skills into the criteria)

```text
/skill-review skills/docs/doc-sync
/skill-review skills/docs/exmd skills/docs/exhtml
/skill-review --propose
```

## Arguments

| Argument    | Effect                                                                                                                       |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `<path>`    | Skill directory or `SKILL.md` to evaluate. Several may be given. Without it, the repository is scanned and the user chooses. |
| `--propose` | Skip evaluation and only confirm criteria candidates noted earlier in the conversation.                                      |

## Behavior

- Checks that the criteria are recorded: `scripts/check_criteria.sh` compares `references/criteria.md` with a recorded baseline, and any change is logged in `references/CHANGELOG.md` after the user confirms it.
- Runs a specification gate (Agent Skills frontmatter and structure, including the description length via `scripts/check_description_length.sh`), then eleven criteria: goal and boundaries, description quality, amount of command examples, completion criteria, early return, self-containment, conciseness, splitting into references, readability, freshness, and client compatibility.
- Description quality includes a trigger test. It drafts about ten scenarios, mixing ones that should select the skill with tricky adjacent ones, and confirms them with the user. Five subagents, given only the names and descriptions of the skills, then answer in parallel which skill they would load. Any scenario answered as expected three times or fewer out of five makes the criterion need improvement. The report shows the count and the breakdown of selected skills for each scenario, the reasons behind unexpected answers, and the tokens the subagents used ([references/trigger-test.md](references/trigger-test.md)).
- Each criterion is judged pass, needs improvement, not applicable, or undetermined. "Needs improvement" always quotes the offending lines and gives a fix.
- Freshness includes running `shellcheck`, `shfmt`, and `ruff` on bundled scripts and executing them with side-effect-free arguments (`--help`, dry-run, read-only). Arguments that write or post are never used.
- Output is a report per skill, with a summary when several skills are evaluated. If the path does not exist or no `SKILL.md` is found, it reports that and stops.
- Does not edit the evaluated skills. The only files it writes are its own `references/CHANGELOG.md`, `scripts/criteria.baseline`, and, for candidates the user approves, `references/criteria.md`.
- After a review, decisions made while fixing skills are collected and confirmed once at a natural break (commit, PR, end of review). Adopted ones update the criteria, the changelog, and the baseline together.

## Dependencies

- `shellcheck`, `shfmt`, and `ruff` for the freshness check of bundled scripts.
- Subagents to run the trigger test.

The full procedure lives in [SKILL.md](SKILL.md). The criteria are in [references/criteria.md](references/criteria.md).
