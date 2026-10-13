# cognitive-rhythm-writing

[日本語](README_ja.md)

Guidelines for designing rhythm and tempo in Japanese expository writing. It is a guideline skill: it takes no arguments and produces no files. An agent loads it while writing or diagnosing prose and follows its rules.

Pacing is treated as the deliberate switching of the reader's cognitive mode (observe, hesitate, assert, re-observe) and the management of unresolved tension, not as decoration. Dense prose turns boring because every sentence is written in the same mode, not because it carries much information.

It layers on top of [`japanese-tech-writing`](../japanese-tech-writing/README.md), the baseline for Japanese prose, for pieces meant to be read through rather than looked up. To remove AI-sounding phrasing from existing text, use [`stop-ai-slop-jp`](../stop-ai-slop-jp/README.md).

## Usage

Use it when generating a chapter, article, or explanation that should be read as a piece, or when diagnosing and fixing text that is "dense but flat and dull" (the description in SKILL.md: "日本語で説明を行う時に使用するskill"). There are no fixed trigger phrases.

## Behavior

The skill covers:

- Sentence beats: set a foothold with a short sentence, flow with a longer one, stop with a short one; alternate assertion and hesitation.
- Density waves across paragraphs: place a sparse paragraph after two or three dense ones, and alternate concrete detail with a step back to meaning.
- How to open a piece and how to enter a section without announcing it.
- Landing enumerations, and returning questions and closing.
- Telling looseness from filler.
- A mechanical post-writing check: topic test, leak test, tension ledger, beat check, boundary check.
- A symptom-to-remedy guide for diagnosing flat text.

Two constraints matter most:

- Material for rhythm comes from the subject itself (events, data, statements, the narrator's state of judgment). Where none exists, nothing is added and the text stays flat. Sentences about the text's own progress ("次は〜") are treated as filler.
- The devices are realized, not declared: the skill's own vocabulary and example sentences must not appear in the body text.

Cutting sentences just to create short beats is forbidden when it removes needed shared context.

## Dependencies

- Builds on [`japanese-tech-writing`](../japanese-tech-writing/README.md).

The full procedure lives in [SKILL.md](SKILL.md).
