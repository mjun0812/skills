# resume-other-agent

[日本語](README_ja.md)

Take the session ID of another coding agent (Codex or Claude Code), find its session log, reconstruct what it was doing from the log plus the current git state, and write a handoff note so the work can continue safely. It is meant for when one agent stopped (rate limit, crash, context loss), not for a full session transplant.

The output is `.ai-handoff/resumed-session.md`, written from `references/resumed-session-template.md`. To ask another agent for an opinion or hand it a new task, use [`claude`](../claude/README.md) or [`codex`](../codex/README.md) instead.

## Usage

- "前回のsessionから再開して"
- "Codexの続きをやって"

```text
/resume-other-agent
/resume-other-agent <session_id>
```

## Arguments

| Argument     | Effect                                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| `session_id` | Session to restore. When omitted, candidate sessions for the current repository are offered. |

## Behavior

- Decide the session ID. When it is not given, offer candidates through `AskUserQuestion`: recent sessions of agents other than the current one that worked in this repository (or cwd), newest first.
- Locate the log by session ID under `${CODEX_HOME:-$HOME/.codex}/sessions/**/*.jsonl` (filtered by the `cwd` field in the log) and `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<cwd-slug>/*.jsonl`. If no log matches, report to the user and stop.
- Check the current state with `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current`, `git status --short`, `git diff --stat`, and `git log --oneline -n 20`.
- Extract from the log: the user's goal and last agreed direction, edited files, executed commands, test/lint/build results, errors and unresolved problems, and next steps. Everything is cross-checked against the current git state.
- Save the result to `.ai-handoff/resumed-session.md`. If the file already exists, ask the user before overwriting.
- Before continuing, report briefly: agent, session ID, log file, confidence, restored goal, files in progress, and the smallest next step.

Safety rules:

- Never output secrets, tokens, API keys, or credentials.
- Use only the log whose session ID matches; do not mix up unrelated sessions.
- Never re-run commands found in the log without verifying them.
- Never continue without checking the git state.
- Do not assert when confidence is low, and do not paste large parts of the log.

## Dependencies

- `git`, `rg`, `jq`

The full procedure lives in [SKILL.md](SKILL.md).
