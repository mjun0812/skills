# research

## deep-research

Research a topic with web search combined with the model's own knowledge, and produce one cited Markdown note in Japanese. The topic is broken into sub-questions, each searched in both English and Japanese with primary sources preferred, and the draft is checked against a quality gate (roughly ten sources across five domains, every sub-question answered, main claims backed by sources) before writing.

| Argument    | Effect                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| `--no-save` | Return the note as the response without offering to save. Required when called from another skill, agent, or `claude -p`. |

The note leads with the conclusion, groups the body by topic, lists unresolved points, and ends with a numbered reference list matched to `[n]` citations in the text. Conflicting sources are reported as conflicts rather than resolved. The prose follows the bundled copies of `japanese-tech-writing` and `stop-ai-slop-jp` in `deep-research/references/`, so the skill is self-contained when installed alone.

Without `--no-save`, the note is shown first and then saved on confirmation as `YYYY-MM-DD_<slug>.md` in the current directory, with frontmatter (`title`, `created`, `updated`, `model`) and any useful figures downloaded into `images/`.

- Trigger phrases: "〜について調べてメモにして", "deep researchして".
- The skill only researches and writes the note. Summarizing, reorganizing, or merging it into other files is out of scope.

The search procedure, quality gate, and note structure live in `SKILL.md`.
