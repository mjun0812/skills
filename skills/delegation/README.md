# delegation

Skills for handing work to another coding agent, or picking up work another agent left behind.

## Which skill to use

| Situation                                                    | Skill                |
| ------------------------------------------------------------ | -------------------- |
| Ask Claude Code for a second opinion, or hand it a task      | `claude`             |
| Ask Codex for a second opinion, or hand it a task            | `codex`              |
| Continue a session that Codex or Claude Code left unfinished | `resume-other-agent` |

`claude` and `codex` are only used when the user names the agent explicitly ("ask Codex", "let Claude do it"). The running agent never invokes them on its own, and never calls itself through them.

## claude

Run the Claude Code CLI non-interactively. Two modes, chosen from how the user phrases the request:

| Mode                   | When                                        | How it runs                                                         |
| ---------------------- | ------------------------------------------- | ------------------------------------------------------------------- |
| Consultation (default) | "ask", "consult", "review"                  | Read-only tools only. The answer is treated as a second opinion.    |
| Delegation             | "let it do", "hand it over", "have it work" | `--permission-mode bypassPermissions` inside the given `--add-dir`. |

The model is picked from the task size (`haiku`, `sonnet`, `opus`; `opus` when unsure). The prompt is written to be self-contained, because the callee has no access to the current conversation. In consultation mode the result is summarized with agreements and disagreements against the caller's own view; in delegation mode the caller reviews the resulting diff.

- Trigger phrases: "Claudeに聞いて", "Claudeに相談して", "Claudeにやらせて", "Claudeに任せて".
- Aborts immediately if the `claude` CLI is not installed or fails to authenticate.

## codex

The Codex counterpart of `claude`, with the same two modes. Consultation runs with sandbox `read-only`, delegation with `workspace-write`, both with `-a never` and web search enabled. Model and reasoning effort are chosen from the task size within the GPT-5.6 family; long-running work is started in the background and polled.

- Trigger phrases: "Codexに聞いて", "Codexに相談して", "Codexにやらせて", "Codexに任せて".
- Aborts immediately if the `codex` CLI is not installed or fails to authenticate.

## resume-other-agent

Locate another agent's session log by session ID, reconstruct what it was doing from the log plus the current git state, and write a handoff note so work can continue safely.

| Argument     | Effect                                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| `session_id` | Session to restore. When omitted, candidate sessions for the current repository are offered. |

Logs are searched under `~/.codex/sessions/` and `~/.claude/projects/`. The reconstructed goal, edited files, executed commands, and next steps are written to `.ai-handoff/resumed-session.md` using `resume-other-agent/references/resumed-session-template.md`. Commands found in the log are never re-run without verification, and secrets are never echoed.

- Trigger phrases: "前回のsessionから再開して", "Codexの続きをやって".

The exact CLI flags and safety rules live in each skill's `SKILL.md`.
