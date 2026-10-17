# skill-review

[English](README.md)

Agent skill(`SKILL.md`と付属ファイル)を固定の評価基準に沿って採点し、観点ごとの判定・根拠・修正案をレポートする。評価だけを行い、修正の適用は別途依頼を待つ。

skillを作成・編集し、agentが実際に従うかを検証するなら[`writing-skills`](../writing-skills/README_ja.md)を使う。

## 使い方

- 「このskillを評価して」
- 「skillをレビューして」
- 「SKILL.mdの品質を見て」
- 「この判断を基準にして」(skillの修正で決まった判断を評価基準へ反映する)

```text
/skill-review skills/docs/doc-sync
/skill-review skills/docs/exmd skills/docs/exhtml
/skill-review --propose
```

## 引数

| 引数        | 効果                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| `<path>`    | 評価対象のskillディレクトリまたは`SKILL.md`。複数指定できる。省略時はリポジトリを探索し、ユーザーに指定を求める。 |
| `--propose` | 評価を行わず、同じ会話で控えた基準候補の確認だけを行う。                                                          |

## 動作

- 評価の前に基準の記録状態を点検する。`scripts/check_criteria.sh`が`references/criteria.md`を記録時点のbaselineと比較し、変更があればユーザーの確認を経て`references/CHANGELOG.md`に記録する。
- 仕様ゲート(Agent Skillsのfrontmatterと構造。descriptionの文字数は`scripts/check_description_length.sh`で判定)を通したあと、11観点で採点する。観点は、目標と境界、description品質、コマンド例の量、完了条件、早期リターン、自己完結性、簡潔さ、分割、可読性、鮮度、クライアント互換性。
- description品質では、trigger testを行う。発動すべき場面と紛らわしい隣接場面を10件前後作ってユーザーに確認し、skill一覧のdescriptionだけを渡したsubagent 5つに、どのskillを読み込むかを並列で答えさせる。期待どおりだったのが5回中3回以下の場面があれば要改善にする。レポートには、場面ごとの回数と選ばれたskillの内訳、期待と違う判定の理由、subagentの消費tokenを載せる([references/trigger-test.md](references/trigger-test.md))。
- 判定は合格・要改善・該当なし・判定保留の4値。要改善には必ず該当行の引用と修正案を付ける。
- 鮮度では、付属scriptに`shellcheck`、`shfmt`、`ruff`を適用し、副作用の無い引数(`--help`、dry-run、読み取り専用)で実行する。書き込みや投稿を伴う引数では実行しない。
- 出力はskillごとのレポートで、複数skillを評価した場合は全体サマリーを付ける。指定パスが存在しない、または`SKILL.md`が見つからない場合は、その旨を報告して終了する。
- 評価対象のskillは編集しない。書き込むのは自skillの`references/CHANGELOG.md`と`scripts/criteria.baseline`、およびユーザーが採用した候補を追記する`references/criteria.md`だけ。
- レビュー後、skillの修正で決まった判断を基準候補として控え、commit・PR・レビュー終了などの区切りで1回だけ確認する。採用された候補は、基準・changelog・baselineを一緒に更新する。

## 依存

- `shellcheck`、`shfmt`、`ruff`: 付属scriptの鮮度確認に使う。
- subagent: trigger testの実行に使う。

手順の詳細は[SKILL.md](SKILL.md)を参照。評価基準は[references/criteria.md](references/criteria.md)にある。
