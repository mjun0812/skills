# grill-me

[日本語](README_ja.md)

Interview the user about a plan or design until no decision point is left. The skill walks the design tree branch by branch and resolves the dependencies between decisions one at a time, going deep on one topic before moving to the next. On finishing, it presents the question-and-answer history.

Use [`grill-self`](../grill-self/README.md) when the agent should decide by itself without asking. For a machine learning experiment plan, use [`experiment-plan`](../experiment-plan/README.md).

## Usage

- "計画を詰めて"
- "計画を改善して"
- "設計を厳しく問い詰めて"
- Also whenever the user wants a plan improved, detailed, or optimized, per the description in SKILL.md.

## Behavior

- Asks exactly one question at a time. Each question carries the agent's recommended answer and its reason, in this template:

```text
### Q[number]: [question]

1. [option]
2. [option]
3. ...

**推奨: [1/2/...]**
**理由:** ...
```

- Questions are posed through a choice tool such as `AskUserQuestion`.
- Before each question, the relevant parts of the codebase are read. Anything the codebase can answer is not asked.
- Depth is preferred over breadth: one topic is explored until it yields no new insight.
- When a topic is exhausted, the skill proposes to finish and continues only if the user asks.
- On finishing, it presents the history of answers, keeping each question paired with its answer.

The skill writes no files.

The full procedure lives in [SKILL.md](SKILL.md).
