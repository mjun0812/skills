# japanese-writing

[日本語](README_ja.md)

Writes or revises Japanese prose under rules chosen for the kind of document.
It merges the rules of [`japanese-tech-writing`](../japanese-tech-writing/README.md) and [`stop-ai-slop-jp`](../stop-ai-slop-jp/README.md) into one skill, and assigns the rules that conflicted to a document kind.
The rules for revising existing text draw on [yomiyasu](https://github.com/nanaism/yomiyasu).

Every reference it needs is bundled in `references/`, so the skill works when installed alone.
[`exhtml`](../../docs/exhtml/README.md) and [`exmd`](../../docs/exmd/README.md) call this skill for prose style when it is installed.

## Usage

- "日本語で記事を書いて"
- "この文章を推敲して"
- "読みやすく直して"
- "AI臭を消して"

It takes no arguments.

## Behavior

1. Decide the kind of document. The kinds are reference, explanation, and personal account. When the document is one of 13 finer kinds such as a PR description, an incident report, minutes, or an email, the skill keeps what is normal for that kind.
2. Decide the kind of work. Writing produces new text, and revision fixes existing text.
3. Read the references for that kind.
4. When writing, check the draft against the structure and vocabulary catalogs and fix it.
5. When revising, read the original once as a first-time reader, then find the problems and fix all of them. Report each change with the quoted original, the revised sentence and the reason.

When rules collide, the skill follows this order.

1. Do not invent facts.
2. Remove AI-sounding prose.
3. Preserve the meaning of each rewritten sentence.

An AI-sounding expression is rewritten when its content can be written out from the original. Otherwise the word or the whole sentence is removed. Removed passages, and passages the writer could fill in with a fact, are reported in the confirmation section.

The references contain the following.

- `references/argument.md`: paragraph and argument structure, rigor, reader load, restraint in rhetoric
- `references/paragraph.md`: paragraph writing for documents that state claims and grounds
- `references/rewriting.md`: rules that decide what to fix and what to keep in existing text
- `references/doc-types.md`: what to keep and what to fix for each of the 13 finer kinds
- `references/markup.md`: when to use tables, lists, diagrams, or prose
- `references/structures.md`: catalog of structures to avoid
- `references/phrases.md`: catalog of vocabulary to avoid

## Dependencies

None.

## Sources

`references/argument.md` draws on k16shikano's [original gist](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d).

`references/rewriting.md` and `references/doc-types.md` draw on [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu).

See [SKILL.md](SKILL.md) for the full procedure.
