# docs

Skills for writing and maintaining documents. Three of them turn a topic into a single readable page, and one keeps existing documentation in step with the code.

## Which skill to use

| Situation                                                   | Skill                              |
| ----------------------------------------------------------- | ---------------------------------- |
| Write down what the current conversation established, as-is | [`chat-note`](chat-note/README.md) |
| Explain a topic in Markdown, researching it first if needed | [`exmd`](exmd/README.md)           |
| Explain a topic as a self-contained HTML page               | [`exhtml`](exhtml/README.md)       |
| Bring existing docs back in line with the implementation    | [`doc-sync`](doc-sync/README.md)   |

`chat-note` never adds outside information. `exmd` and `exhtml` may research the topic and share the same structure (summary, glossary, body, figures); they differ only in output format.
