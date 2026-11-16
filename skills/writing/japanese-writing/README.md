# japanese-writing

[日本語](README_ja.md)

Writes or revises Japanese prose under rules chosen for the kind of document.
It merges the rules of [`japanese-tech-writing`](../japanese-tech-writing/README.md), [`cognitive-rhythm-writing`](../cognitive-rhythm-writing/README.md), and [`stop-ai-slop-jp`](../stop-ai-slop-jp/README.md) into one skill, and assigns the rules that conflicted among the three to a document kind.

Every reference it needs is bundled in `references/`, so the skill works when installed alone.

## Usage

- "日本語で記事を書いて"
- "この文章を推敲して"
- "読みやすく直して"
- "AI臭を消して"

It takes no arguments.

## Behavior

1. Decide the kind of document. The kinds are reference, explanation, and personal account.
2. Decide the kind of work. Writing produces new text, and revision fixes existing text.
3. Read the references for that kind.
4. When writing, check the draft against the structure and vocabulary catalogs and fix it. An explanation also goes through the rhythm checklist.
5. When revising, fix every problem found. Then report each change with the quoted original, the revised sentence and the reason. An AI-sounding expression whose content cannot be written out is removed, word or sentence, and the removal is reported.

The rules that change with the kind of document are as follows.

| Kind             | Documents                                               | Example rules                                                                                  |
| ---------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Reference        | References, procedures, READMEs, specs, PRs, reports    | Open with the subject and its premises. State prohibitions flatly with a reason. Add no rhythm |
| Explanation      | Technical articles, book chapters, explanations, essays | May open with a question drawn from the subject. Headings may be questions. Design the rhythm  |
| Personal account | Blog posts, essays, personal accounts, retrospectives   | Open with the writer's own story. Keep hedges that convey confidence, and remove disclaimers   |

A fix may need a new fact such as an actor, a number or a spec. The skill does not guess that fact. It removes the word or the sentence and lists it in the confirmation section of the report.

The references contain the following.

- `references/argument.md`: paragraph and argument structure, rigor, reader load, restraint in rhetoric
- `references/rhythm.md`: rhythm design for explanations and the post-writing checklist
- `references/structures.md`: catalog of structures to avoid
- `references/phrases.md`: catalog of vocabulary to avoid

## Dependencies

None.

## Sources

`references/argument.md` draws on k16shikano's [original gist](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d), and `references/rhythm.md` draws on another [original gist](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432) by the same author.

The rules for preserving the meaning of a rewritten sentence draw on [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu).

See [SKILL.md](SKILL.md) for the full procedure.
