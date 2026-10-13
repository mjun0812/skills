# japanese-tech-writing

[日本語](README_ja.md)

Writing rules for Japanese technical documents and book manuscripts. It is a guideline skill: it takes no arguments and produces no files. An agent loads it while writing or revising a chapter, draft, article, or explanation in Japanese and follows its rules.

It is the baseline for new Japanese writing and is what [`exhtml`](../../docs/exhtml/README.md) and [`exmd`](../../docs/exmd/README.md) defer to for prose style. For pieces meant to be read through rather than looked up, layer [`cognitive-rhythm-writing`](../cognitive-rhythm-writing/README.md) on top. To clean up AI-sounding text that already exists, use [`stop-ai-slop-jp`](../stop-ai-slop-jp/README.md).

## Usage

Use it when writing or revising Japanese technical text, as in the SKILL.md description: "日本語で技術書の章、草稿、記事、解説文を書くとき、または推敲・リライトするとき". There are no fixed trigger phrases.

## Behavior

The skill sets rules in these areas:

- Formatting: one sentence per line, code blocks for code and logs, footnotes for side remarks, bold for terms when first defined (and 「」 for later mentions). No dashes (em dash, horizontal bar) and no middle dots (・) in running Japanese text or headings; headings are single natural phrases.
- Paragraphs and argument structure (paragraph writing): one topic per paragraph, with explicit logical connectives.
- Rigor of argument: remove points a reader could attack, such as unqualified causation, lumping distinct things together, and forward references that are never paid off.
- Reader load, narrative stance, and restraint in dramatization.
- No LLM-style filler: announcements and summaries ("本章では〜を扱う"), "正面から" phrases, empty adjectives and verbs, chained connectives, unfounded hedging and praise.
- Removing redundancy, writing concrete headings in the source language, and honesty toward the reader (not hiding that an example may look contrived, not writing as if unchecked things were checked).

The full procedure lives in [SKILL.md](SKILL.md).
