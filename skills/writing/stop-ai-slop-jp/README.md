# stop-ai-slop-jp

[日本語](README_ja.md)

Revise AI-written Japanese (blog posts, essays, experience reports, notes, technical documents) into natural, readable prose. It treats the core of "AI smell" as the absence of a writer (no stance, no agency, no concrete experience), not as symbols or emoji. The two goals are removing the AI smell and improving readability; when they conflict, readability wins. It does not add human-sounding quirks as decoration.

The check runs from meaning down to surface: stance and agency, structure, sentences and paragraphs, vocabulary and symbols, then readability. The output is a scored report with numbered fixes. The skill has no rules for writing from scratch; for that, use [`japanese-tech-writing`](../japanese-tech-writing/README.md) or [`cognitive-rhythm-writing`](../cognitive-rhythm-writing/README.md).

Revision follows the audience and document type. For technical documents, clarify the subject, conditions, operations, and outcomes while preserving established terminology and tables that support lookup. Do not require personal reflections or stylistic variation based on criteria for experience reports.

## Usage

- "AI臭を消して"
- "この文章を人間が書いたように直して"
- "AIっぽさを直して"

## Behavior

1. Identify the audience, document type, and existing terminology and spelling conventions, then find problems in the order stance and agency, structure, sentences and paragraphs, vocabulary and symbols, readability. Each problem quotes the original text.
2. Score six axes from 0 to 10 (higher is better): stance, agency, concreteness, rhythm, concision, readability (total 0 to 60).
3. Output the report: a verdict (summary of 200 characters or fewer, and whether revision is needed), the score table, major fixes, and recommended fixes, numbered consecutively. Revision is "needed" when there is at least one major fix or any axis scores 6 or below.
4. The user picks the fixes to apply by number. Only the chosen fixes are applied; nothing else is changed.
5. Compare the revision with the original for remaining vague terms and lost specification details. When changing terminology, align meaning and spelling in headings, prose, tables, diagrams, link labels, and sidebars within the approved editing scope. Preserve code identifiers and actual UI labels, and report any needed changes outside that scope.

Major versus recommended is decided by whether the problem hinders understanding. Structural and stance problems, repeated standalone negations, labels that anticipate the reader's reaction, and unresolvable references are major; vocabulary and symbol issues and minor structural padding are recommended.

Safety rule: a fix that needs a new fact (an actor, number, proper noun, or episode) is never filled in by guessing. It is raised as a question to the writer, such as "要確認: この方針は誰が決めたか". If the writer has no concrete story, the skill does not invent one.

For technical documents, also review vague simplifications, ambiguous personification, and unnecessary time qualifiers that imply future support. Reference headings generally use noun phrases naming their subject and content. Remove elementary explanations the audience does not need and command options that merely restate defaults. Separate exceptional cases from the main procedure while keeping necessary prerequisites and warnings. Treat textlint results as review cues; the presence or absence of warnings does not determine whether prose is natural.

The pattern catalogs are `references/structures.md` (six families of structures to avoid) and `references/phrases.md` (nine families of vocabulary to eliminate). They collect the habits of current models and are neither exhaustive nor permanent; signs outside the lists are still flagged when they tie to the writer's absence or hinder understanding.

## Dependencies

None.

The full procedure lives in [SKILL.md](SKILL.md).
