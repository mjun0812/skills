# resume-other-agent

[English](README.md)

別のcoding agent(CodexまたはClaude Code)のsession IDを受け取り、そのsessionログを特定する。ログと現在のgit状態から直前の作業を復元し、安全に続行するための引き継ぎメモを書く。agentが止まった(rate limit / crash / context loss)ときのためのskillで、sessionを丸ごと移植するものではない。

出力は`.ai-handoff/resumed-session.md`で、`references/resumed-session-template.md`の書式で書く。別のagentに意見を求める、または新しい作業を渡す場合は[`claude`](../claude/README_ja.md)または[`codex`](../codex/README_ja.md)を使う。

## 使い方

- "前回のsessionから再開して"
- "Codexの続きをやって"

```text
/resume-other-agent
/resume-other-agent <session_id>
```

## 引数

| 引数         | 効果                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| `session_id` | 復元対象のsession。省略した場合は、現在のrepositoryの候補sessionを提示する。 |

## 動作

- session IDを決める。渡されていなければ`AskUserQuestion`で候補を提示する。候補は、自分以外のagentのsessionのうち、現在のrepository(またはcwd)で作業していたものを新しい順に挙げる。
- session IDでログを特定する。探す場所は`${CODEX_HOME:-$HOME/.codex}/sessions/**/*.jsonl` (ログ内の`cwd`フィールドで絞り込む)と`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<cwd-slug>/*.jsonl`である。該当するログがなければユーザーに報告して止まる。
- `pwd`、`git rev-parse --show-toplevel`、`git branch --show-current`、`git status --short`、`git diff --stat`、`git log --oneline -n 20`で現状を確認する。
- ログからユーザーの目的と最後に合意された方針、編集ファイル、実行済みコマンド、test・lint・build結果、エラーや未解決の問題、次にやるべき作業を抜き出す。すべて現在のgit状態で確かめる。
- 結果を`.ai-handoff/resumed-session.md`に保存する。既に存在する場合は、上書きする前にユーザーに確認する。
- 続行前に短く報告する。内容は、読んだagent、session ID、ログファイル、confidence、復元した目的、変更中ファイル、次の最小ステップである。

安全規則:

- secret、token、API key、credentialを出力しない。
- session IDが一致するログだけを使い、関係ないsessionと混同しない。
- ログ内のコマンドを検証なしに再実行しない。
- git状態を確認せずに続行しない。
- confidenceが低い場合は言い切らず、ログ全文を大量に貼らない。

## 依存

- `git`、`rg`、`jq`

手順の詳細は[SKILL.md](SKILL.md)を参照。
