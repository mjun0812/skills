# yomiyasu-lite

[日本語](README_ja.md)

Revise AI-written Japanese, touching only the places the bundled lint flags, without changing the meaning. The lint flags wording such as unnatural metaphorical verbs, words common in AI output, and boilerplate openings and closings. It also flags formatting such as excessive bold and bullet lists, emoji, dashes, and trailing colons. Sentences without a warning are left as they are, even if they look hard to read.

Each fix keeps the claim and the strength of assertion of the original. It also keeps the facts (numbers, proper nouns, and conditions) and who does what. It adds no information that is not in the original. If no rewrite keeps all of this, the original stays. If the meaning is unclear, the point becomes a question to the writer. The skill does not fix structural problems the lint misses, such as a predicate that does not match its subject.

To remove the AI feel from the whole text and get a score, use [`stop-ai-slop-jp`](../stop-ai-slop-jp/README.md).

## Usage

This skill has `disable-model-invocation: true`. It runs only when the user calls `/yomiyasu-lite`; the running agent never invokes it on its own.

- `/yomiyasu-lite draft.md`
- `/yomiyasu-lite` followed by pasted text

## Behavior

1. Run the bundled lint on the original. When the document type is known (for example a PR or an incident report), pass it so that writing that is normal for that type is not flagged.
2. Judge each candidate one by one, and keep the ones that meet the "may keep" condition stated in the warning.
3. Rewrite the remaining candidates while keeping the meaning.
4. Run the lint again on the final draft, and give a reason for each warning that remains.

The final draft is saved next to the original as `<original name>.yomiyasu.md`, and the original is not modified. The original is overwritten only when the user asks for it. The reply shows the save path and the rewritten text, with the changes, remaining warnings, and questions for the writer. The skill does not commit, push, or post anywhere.

## Dependencies

- Python 3.14 or later (`python3`). The bundled scripts use only the standard library.

The bundled lint (`scripts/`) is adapted from `yomiyasu_lint.py` and `markdown_visibility.py` in [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) v2.0.1 (MIT License, see [LICENSE](LICENSE); for the Unicode data used to detect emoji, see [UNICODE-LICENSE.txt](UNICODE-LICENSE.txt)).

The full procedure lives in [SKILL.md](SKILL.md).
