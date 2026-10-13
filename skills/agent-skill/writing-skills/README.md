# writing-skills

[日本語](README_ja.md)

Create or edit an agent skill test-first. Run a pressure scenario with a subagent before the skill exists and record how it fails, write the skill against those failures, then rerun until the subagent complies and close the loopholes it found. It applies the red-green-refactor cycle of test-driven development to skill documents.

To score an existing skill against fixed criteria, use [`skill-review`](../skill-review/README.md) instead. `skill-review` scores a finished skill; `writing-skills` checks whether agents actually follow it.

## Usage

- 「skillを作って」
- 「このskillを直して」
- Verifying a skill's behavior before deployment

## Behavior

- Defines test cases as pressure scenarios run by subagents, observes the baseline failure without the skill, writes the minimum skill that addresses those failures, and verifies compliance.
- Refactors by finding new excuses the agent uses, closing them, and re-verifying.
- Covers skill types (technique, pattern, reference), directory layout, `SKILL.md` structure, and description optimization for discovery.
- Personal skills go in the skills directory of the runtime (`~/.claude/skills/` for Claude Code).
- The test-driven development background it requires is bundled in `references/test-driven-development.md`, so it is read only from this skill and is not triggered on its own for regular implementation work.
- Other bundled references: `anthropic-best-practices.md`, `testing-skills-with-subagents.md`, `persuasion-principles.md`, and `CLAUDE_MD_TESTING.md`.

## Dependencies

- Subagents, used to run the baseline and compliance scenarios.
- Optional: `scripts/render-graphs.js` renders the `dot` diagrams in a `SKILL.md` to SVG and requires Graphviz (`dot`).

Adapted from the `writing-skills` skill in obra/superpowers v6.4.2 (MIT License, see [LICENSE](LICENSE)).

The full procedure lives in [SKILL.md](SKILL.md).
