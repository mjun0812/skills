# claude

[English](README.md)

Claude Code CLIを非対話モードで呼び出し、相談への回答または委譲した作業の結果を得る。デフォルトはread-onlyの相談モードで、ユーザーが作業の実行を明示的に依頼したときだけ編集権限付きで実行する。

Claude Codeへ渡す場合のskillである。Codexへ渡す場合は[`codex`](../codex/README_ja.md)を使う。別のagentが中断したsessionを引き継ぐ場合は[`resume-other-agent`](../resume-other-agent/README_ja.md)を使う。

## 使い方

`disable-model-invocation: true`のskillである。ユーザーがagentを名指ししたときだけ実行し、実行中のagentが自発的に呼ぶことはない。実行中のagent自身がClaude Codeの場合も使わない。

- "Claudeに聞いて"
- "Claudeに相談して"
- "Claudeにやらせて"
- "Claudeに任せて"

## 動作

依頼の言い方でモードを決める。

| モード                 | 条件                                   | 実行方法                                                                                                               |
| ---------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 相談モード(デフォルト) | 「聞いて」「相談して」「レビューして」 | read-only: `--tools "Read,Grep,Glob"`、`--disallowedTools "Edit,Write,Bash"`、`--permission-mode dontAsk`、`--add-dir` |
| 委譲モード             | 「やらせて」「任せて」「作業させて」   | `--permission-mode bypassPermissions`。`--add-dir`で作業対象ディレクトリへのアクセスを許可する                         |

判断に迷う場合は相談モード(read-only)を選ぶ。

- モデルは作業の大きさに応じて`--model`で指定する。`haiku` (軽い修正・定型的な作業)、`sonnet` (通常の作業・調査・レビュー・実装)、`opus` (重い作業・複雑な判断)。迷った場合は`opus`。
- 相手はこの会話の文脈を知らないため、プロンプトは自己完結させる。背景と関連ファイルパスに加え、相談モードでは質問を、委譲モードでは成功条件を含める。
- CLIは`-p`と`--no-session-persistence`付きで実行する。
- 相談モード: 回答は第二意見として扱う。回答をそのまま転送せず、要点と根拠を整理し、呼び出し元の見解との一致点・相違点を添えて提示する。最終判断は呼び出し元のagentが行う。
- 委譲モード: すべてのツール(Edit/Write/Bash等)を自動許可する。実行結果と変更箇所を提示し、呼び出し元のagentが差分を確認して必要なら追加修正する。
- `claude` CLIが未導入(`which claude`が失敗)、または認証やpermissionのエラーで実行できない場合は、直ちに中止してユーザーに伝える。

## 依存

- `claude` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
