# rule-lint

[日本語](README_ja.md)

Converts coding conventions written as prose in `CLAUDE.md`, steering, ADRs, or review comments into mechanical checks with linter settings, ast-grep, or scripts.
A unit of work is not just writing the check: it includes verifying it with tests and wiring it into git hooks and CI.

## Usage

- "規約をlintにして"
- "ルールを機械的にチェックできるようにして"
- "何度も指摘していることを自動チェックにして"

```text
/rule-lint
```

## Behavior

- Collects conventions. Without a specified source, it reads `CLAUDE.md`, `AGENTS.md`, `.mjun/steering/`, ADRs, and the conventions section of the README. From review comments, only those raised two or more times are targeted.
- Classifies each convention as "full", "partial", or "not checkable".
- Chooses the check mechanism in this order: an existing linter rule, an ast-grep rule, a script.
- Gives each check a message that says how to fix the violation, and a test. Exceptions go into per-file excludes in the config with a reason; inline suppression comments are not used.
- Wires the checks into both git hooks and CI. If the repository has agent hooks, the checks are added there too.
- If existing code has violations, asks the user to choose among "fix them", "record them as a baseline", and "start as warnings".
- Updates the convention documents to match the classification. For "partial" conventions, the prose stays and the range the check misses is written next to it. ADRs are never rewritten or deleted, because a check replaces the prose rule but not the recorded rationale and history; an `Enforced by:` line pointing at the check is added instead. If a new convention would be needed, it is proposed instead of being written into the documents.

## Dependencies

- A linter for the target repository's language (ruff, eslint, etc.)
- [ast-grep](https://ast-grep.github.io/)

The full procedure lives in [SKILL.md](SKILL.md).
