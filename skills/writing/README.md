# writing

Guideline skills for Japanese prose. They carry no arguments and produce no files on their own: an agent loads one while writing or revising and follows its rules.

## Which skill to use

| Situation                                                                  | Skill                      |
| -------------------------------------------------------------------------- | -------------------------- |
| Write or revise a technical document, book chapter, or article in Japanese | `japanese-tech-writing`    |
| Make dense expository prose readable by designing its rhythm               | `cognitive-rhythm-writing` |
| Remove the "written by AI" feel from an existing Japanese text             | `stop-ai-slop-jp`          |

`japanese-tech-writing` is the baseline for new writing and is what `exhtml`, `exmd`, and `deep-research` defer to for prose style. `cognitive-rhythm-writing` layers on top of it for pieces meant to be read through rather than looked up. `stop-ai-slop-jp` is a revision tool and has no rules for writing from scratch.

## japanese-tech-writing

Rules for Japanese technical writing: formatting (one sentence per line, code blocks, footnotes, no dashes or middle dots in running text), paragraph writing with one topic per paragraph and explicit logical connectives, rigor of argument (no unqualified causation, no lumping distinct things together, forward references that are actually paid off), reader load, narrative stance, restraint in dramatization, and elimination of filler phrases typical of LLM output.

- Use when writing or revising a chapter, draft, article, or explanation in Japanese.

## cognitive-rhythm-writing

Treats pacing as the deliberate switching of the reader's cognitive mode (observe, hesitate, assert, re-observe) and the management of unresolved tension, rather than as decoration. Covers sentence beats, paragraph density waves, how to open a piece and enter a section without announcing it, landing enumerations, telling looseness from filler, and a mechanical post-writing check. Material for rhythm must come from the subject itself; sentences about the text's own progress are treated as filler.

- Use for chapters, articles, and explanations meant to be read as a piece, or to diagnose prose that is dense but flat.

## stop-ai-slop-jp

Revise AI-written Japanese (blog posts, essays, notes, technical docs) into natural, readable prose. The check runs from meaning down to surface: stance and agency, structure, sentences and paragraphs, vocabulary and symbols, readability. Each finding quotes the original, and the text is scored 0 to 10 on stance, agency, concreteness, rhythm, concision, and readability. The user then picks which numbered fixes to apply; nothing else is changed. Suggested fixes never invent facts the writer did not supply.

The pattern catalogs are in `stop-ai-slop-jp/references/structures.md` and `references/phrases.md`.

- Trigger phrases: "AI臭を消して", "この文章を人間が書いたように直して", "AIっぽさを直して".

The full rule sets live in each skill's `SKILL.md`.
