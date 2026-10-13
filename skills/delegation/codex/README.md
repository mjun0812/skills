# codex

[日本語](README_ja.md)

Run the Codex CLI non-interactively to get an answer to a question or the result of delegated work. It is the Codex counterpart of [`claude`](../claude/README.md) with the same two modes. The default is a read-only consultation; edit permission is granted only when the user explicitly asks for the work to be carried out.

To hand work to Claude Code instead, use [`claude`](../claude/README.md). To pick up a session another agent left unfinished, use [`resume-other-agent`](../resume-other-agent/README.md).

## Usage

The skill has `disable-model-invocation: true`. It runs only when the user names the agent explicitly; the running agent never invokes it on its own, and it is not used when the running agent is itself Codex.

- "Codexに聞いて"
- "Codexに相談して"
- "Codexにやらせて"
- "Codexに任せて"

## Behavior

The mode is chosen from how the request is phrased.

| Mode                   | When                                        | Sandbox           |
| ---------------------- | ------------------------------------------- | ----------------- |
| Consultation (default) | "ask", "consult", "review"                  | `read-only`       |
| Delegation             | "let it do", "hand it over", "have it work" | `workspace-write` |

When unsure, consultation (read-only) is chosen. Both modes run `codex exec` with `-a never` and `--search` (web search enabled).

- Model and thinking effort are picked from the task size, only within the GPT-5.6 family:

| Task                                                         | Model           | Effort   |
| ------------------------------------------------------------ | --------------- | -------- |
| Light checks, routine consultation, small fixes              | `gpt-5.6-luna`  | `medium` |
| Normal work, investigation, review, implementation           | `gpt-5.6-luna`  | `xhigh`  |
| Design decisions, ambiguous requirements, hard debugging     | `gpt-5.6-terra` | `high`   |
| Especially hard decisions, large implementation, deep review | `gpt-5.6-sol`   | `xhigh`  |

- When unsure, `gpt-5.6-luna` with `xhigh`. If `xhigh` fails, it is rerun with `high`.
- The prompt is written to be self-contained, because the callee cannot see the current conversation: background, relevant file paths, and the question (consultation) or the success criteria (delegation).
- Work expected to take more than a few minutes is started with `run_in_background` and polled with `BashOutput` until it finishes.
- Consultation: the answer is a second opinion. The skill summarizes its points and grounds, and states where it agrees or disagrees with the caller's own view instead of forwarding the answer verbatim. The final judgment stays with the calling agent.
- Delegation: runs without asking for approval (`-a never`). The skill reports the result and the changed files, and the caller reviews the resulting diff and fixes it if needed.
- If the `codex` CLI is not installed (`which codex` fails), or authentication or permissions fail, the skill aborts immediately and tells the user.

## Dependencies

- `codex` CLI

The full procedure lives in [SKILL.md](SKILL.md).
