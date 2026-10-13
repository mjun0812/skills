# claude

[日本語](README_ja.md)

Run the Claude Code CLI non-interactively to get an answer to a question or the result of delegated work. The default is a read-only consultation; edit permission is granted only when the user explicitly asks for the work to be carried out.

The skill is for hand-offs to Claude Code. To hand work to Codex instead, use [`codex`](../codex/README.md). To pick up a session another agent left unfinished, use [`resume-other-agent`](../resume-other-agent/README.md).

## Usage

The skill has `disable-model-invocation: true`. It runs only when the user names the agent explicitly; the running agent never invokes it on its own, and it is not used when the running agent is itself Claude Code.

- "Claudeに聞いて"
- "Claudeに相談して"
- "Claudeにやらせて"
- "Claudeに任せて"

## Behavior

The mode is chosen from how the request is phrased.

| Mode                   | When                                        | How it runs                                                                                                            |
| ---------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Consultation (default) | "ask", "consult", "review"                  | Read-only: `--tools "Read,Grep,Glob"`, `--disallowedTools "Edit,Write,Bash"`, `--permission-mode dontAsk`, `--add-dir` |
| Delegation             | "let it do", "hand it over", "have it work" | `--permission-mode bypassPermissions` with `--add-dir` limiting access to the target directory                         |

When unsure, consultation (read-only) is chosen.

- The model is picked from the task size with `--model`: `haiku` (light, routine), `sonnet` (normal work, investigation, review, implementation), `opus` (heavy or complex work). When unsure, `opus`.
- The prompt is written to be self-contained, because the callee cannot see the current conversation: background, relevant file paths, and the question (consultation) or the success criteria (delegation).
- The CLI runs with `-p` and `--no-session-persistence`.
- Consultation: the answer is a second opinion. The skill summarizes its points and grounds, and states where it agrees or disagrees with the caller's own view instead of forwarding the answer verbatim. The final judgment stays with the calling agent.
- Delegation: all tools (Edit, Write, Bash, ...) are auto-approved. The skill reports the result and the changed files, and the caller reviews the resulting diff and fixes it if needed.
- If the `claude` CLI is not installed (`which claude` fails), or authentication or permissions fail, the skill aborts immediately and tells the user.

## Dependencies

- `claude` CLI

The full procedure lives in [SKILL.md](SKILL.md).
