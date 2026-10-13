# deep-research

[日本語](README_ja.md)

Researches a topic by combining the model's own knowledge with thorough web search, and produces one cited Markdown note in Japanese. The note is shown first and saved to the current directory only if you confirm.

The skill only researches and writes the note. Summarizing, reorganizing, or merging the note into other files is out of scope.

## Usage

- "〜について調べてメモにして"
- "deep researchして"

```text
/deep-research Rust async runtimes comparison
/deep-research --no-save WebGPU adoption status
```

## Arguments

| Argument    | Effect                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| `--no-save` | Return the note as the response without offering to save. Required when called from another skill, agent, or `claude -p`. |

## Behavior

- Confirms the scope. It asks 2-3 questions only when the topic is ambiguous enough to split the approach; if no topic is given it asks for one and exits.
- Breaks the topic into 3-8 sub-questions and searches each in both English and Japanese, preferring primary sources (official docs, papers, announcements) and reading the pages rather than only the result lists.
- Checks a quality gate before writing: roughly 10 or more sources across 5 or more domains, every sub-question answerable, and the main claims backed by sources. If the topic is narrow and sources are structurally few, it does not pad the count and says so in the report.
- Looks for gaps, counterexamples, and recent changes before drafting.
- The note leads with the conclusion, groups the body by topic, lists unresolved points, and ends with a numbered reference list matched to `[n]` citations in the text. Conflicting sources are reported as conflicts, not resolved toward one side.
- The prose follows the bundled copies of `japanese-tech-writing` and `stop-ai-slop-jp` in `references/`, so the skill is self-contained when installed alone.
- Without `--no-save`, it shows the note, asks whether to save, then writes `YYYY-MM-DD_<slug>.md` in the current directory with frontmatter (`title`, `created`, `updated`, `model`). Useful figures are downloaded into `images/` and linked by relative path.
- After saving, it formats the file with `oxfmt` and checks that citations match the reference list and that image links resolve.
- It does not depend on any one agent's tools, so it works in coding agents other than Claude Code.

## Dependencies

- `oxfmt` (to format the saved note)

The full procedure lives in [SKILL.md](SKILL.md).
