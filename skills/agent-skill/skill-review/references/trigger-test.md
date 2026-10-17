# trigger test

descriptionだけを読んだagentが、場面ごとに対象skillを選ぶかどうかを確かめる。
観点2 (description品質) の判定の根拠にする。

## 場面を作る

対象skillのdescriptionと、手順1で列挙した他skillのdescriptionから、10件前後の場面を作る。

- 発動すべき場面を半分ほど入れる。依頼の言い回しを変えたもの、skill名やファイル形式を明示しないもの、ユーザーの依頼ではなく作業の途中でagent自身が判断する場面を混ぜる
- 発動すべきでない場面を半分ほど入れる。対象skillと語や題材が重なるが、別のskillで扱うべき場面か、どのskillも要らない場面にする。無関係で明らかに外れる場面は入れない
- 各場面に、期待するskill名 (どのskillも要らなければ「なし」) を付ける

場面と期待をユーザーに提示し、AskUserQuestionで「この場面で実行する」か「場面を直す」かを確認してから実行する。
同じ会話でdescriptionを直したあとに再テストするときは、確認済みの場面をそのまま使い、確認を省く。

## 実行する

次のpromptを組み立て、subagent 5つに同じものを並列に渡す。
skill一覧には、対象skillと手順1で列挙した他skillを、`name` と `description` のまま並べる。
subagentのmodelは、対象skillを実際に使うagentと同じものを指定する。

```text
あなたはcoding agentで、次のskillが使える (名前: description)。skillは、descriptionから今の作業に合うと判断したときだけ読み込む。

- <name>: <description>
- ...

次の場面それぞれについて、独立に判断し、読み込むskill名 (なければ「なし」) と1行の理由を答えよ。実際の作業はせず、toolも使わないこと。
最終メッセージは、各場面について1行ずつ `番号<TAB>skill名<TAB>理由` の形式だけで返せ。

1. <場面>
2. ...
```

## 別のclientでも試す

skillはClaude CodeとCodexの両方で使われるため、main sessionと別のclientのCLIでも、同じpromptを5回試す。
main sessionがClaude Codeなら `codex exec` を、Codexなら `claude -p` を使う。
1回の応答でBashの呼び出しを5つ並べて並列に実行し、promptは引用符付きのheredocで標準入力から渡す。

```bash
codex exec --sandbox read-only --ephemeral --skip-git-repo-check --json - <<'PROMPT'
<prompt>
PROMPT
```

答えは `"type":"agent_message"` の `text` にある。消費tokenは `turn.completed` の `usage` の `input_tokens` と `output_tokens` の和とする。使ったモデルは出力に含まれないため、`$CODEX_HOME/config.toml` (既定は `~/.codex/config.toml`) の `model` と `model_reasoning_effort` を読む。

```bash
claude -p --tools "" --disable-slash-commands --strict-mcp-config --no-session-persistence --output-format json <<'PROMPT'
<prompt>
PROMPT
```

答えは `result` にある。消費tokenは `usage` の `input_tokens`・`cache_creation_input_tokens`・`cache_read_input_tokens`・`output_tokens` の和とする。使ったモデルは `modelUsage` のキーにある。

- コマンドが見つからない、または認証のエラーで失敗したら、別のclientのテストはskipし、skipした理由をレポートに書く
- sandboxの通信制限で失敗したら、ユーザーの承認を得てsandboxの外で実行する
- どちらのCLIもユーザー設定 (global instructionsなど) を読み込むため、subagentより文脈が多い。期待と違う判定の理由がその設定に由来する場合は、レポートにそう書く

## 判定する

clientごと、場面ごとに、5回のうち期待どおりのskillが選ばれた回数を数える。

- 試したすべてのclientで、すべての場面が4回以上: 観点2のtrigger testは合格
- どれかのclientで3回以下の場面がある: 観点2を要改善にする。根拠には、そのclient、場面、回数、期待と違う判定の理由を引用する。修正案は、理由に挙がったdescriptionの語句を直す形で書く

## レポートに載せる

レポートの「trigger test」に、次の4つを載せる。

- 場面ごとの表: 場面、期待、clientごとの期待どおりだった回数と選ばれたskillの内訳 (例: `duckdb 3 / なし 2`)
- 期待と違う判定の理由: 該当したclientと場面ごとに、答えた理由をそのまま引用する
- 消費token: clientごとに、1回ごとと合計のtoken数を書く。subagentは完了時に返る使用量を使い、返らなければ「不明」と書く
- 使ったモデル: clientごとに書く。subagentは起動時に指定したモデルを書く

再テストでは、直す前と直した後の回数と内訳を同じ表に並べ、消費tokenと使ったモデルも両方を書く。
