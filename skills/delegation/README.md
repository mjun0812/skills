# delegation

Skills for handing work to another coding agent, or picking up work another agent left behind.

## Which skill to use

| Situation                                                    | Skill                                                |
| ------------------------------------------------------------ | ---------------------------------------------------- |
| Ask Claude Code for a second opinion, or hand it a task      | [`claude`](claude/README.md)                         |
| Ask Codex for a second opinion, or hand it a task            | [`codex`](codex/README.md)                           |
| Continue a session that Codex or Claude Code left unfinished | [`resume-other-agent`](resume-other-agent/README.md) |

`claude` and `codex` are only used when the user names the agent explicitly ("ask Codex", "let Claude do it"). The running agent never invokes them on its own, and never calls itself through them.
