# writing

Skills for Japanese prose. The guideline skills carry no arguments and produce no files on their own: an agent loads one while writing or revising and follows its rules. `yomiyasu-lite` is a revision tool that only the user invokes.

## Which skill to use

| Situation                                                                       | Skill                                                            |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Write or revise a technical document, book chapter, or article in Japanese      | [`japanese-tech-writing`](japanese-tech-writing/README.md)       |
| Make dense expository prose readable by designing its rhythm                    | [`cognitive-rhythm-writing`](cognitive-rhythm-writing/README.md) |
| Remove the "written by AI" feel from an existing Japanese text                  | [`stop-ai-slop-jp`](stop-ai-slop-jp/README.md)                   |
| Fix only the lint-flagged spots in a Japanese text without changing its meaning | [`yomiyasu-lite`](yomiyasu-lite/README.md)                       |

`japanese-tech-writing` is the baseline for new writing and is what `exhtml`, `exmd`, and `deep-research` defer to for prose style. `cognitive-rhythm-writing` layers on top of it for pieces meant to be read through rather than looked up. `stop-ai-slop-jp` is a revision tool and has no rules for writing from scratch. `yomiyasu-lite` also revises, but it changes only the spots its bundled lint flags, so it suits texts whose facts must stay exactly as written.
