# grill-self

[日本語](README_ja.md)

Resolve every decision point of a plan or design through the agent's own research and self-questioning. The skill walks the same design tree as [`grill-me`](../grill-me/README.md), depth before breadth, but never asks the user a question: each branch point is decided with reasons, and a decision log is presented at the end.

Use [`grill-me`](../grill-me/README.md) when the user wants to be asked and to decide.

## Usage

- "自分で判断して計画を詰めて"
- "質問せずに設計を詰めて"
- "セルフgrillして"
- "grill-selfして"

## Behavior

Decisions are made one at a time, never several at once. Before each decision, the codebase, existing conventions, and documents are checked instead of guessing. Each branch point goes through these steps:

1. Question: state in one sentence what is being decided.
2. Research: gather the evidence.
3. Proposal: form a proposal with reasons.
4. Counter-argument: raise and examine at least one counter-argument (devil's advocate) before adopting, to avoid self-affirming decisions.
5. Adoption: decide, and record a confidence of high, medium, or low.

Value judgments that research cannot settle (for example, whether to drop backward compatibility) are provisionally adopted with the recommended proposal at confidence low, instead of blocking on a question. The walk ends when no topic produces new points.

Output at the end:

- A decision log table with the columns question, decision, reason, and confidence.
- Low-confidence items listed again as "needs confirmation" after the table, each with a one-line note on what would be affected if the decision is overturned.

The skill writes no files.

The full procedure lives in [SKILL.md](SKILL.md).
