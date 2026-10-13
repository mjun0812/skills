# writing-skills

[English](README.md)

agent skillをテストファーストで作成・編集する。skillが存在しない状態でsubagentにプレッシャーシナリオを実行して失敗の様子を記録し、その失敗に対処するskillを書き、subagentが従うようになるまで再実行して、見つかった抜け道を塞ぐ。テスト駆動開発のRED-GREEN-REFACTORサイクルをskill文書に適用したもの。

既存のskillを固定の基準で採点するなら[`skill-review`](../skill-review/README_ja.md)を使う。`skill-review`は完成したskillを採点し、`writing-skills`はagentが実際に従うかを検証する。

## 使い方

- 「skillを作って」
- 「このskillを直して」
- deploy前にskillの動作を確かめるとき

## 動作

- テストケースをsubagentによるプレッシャーシナリオとして定義し、skillなしのbaselineの失敗を観察し、その失敗に対処する最小限のskillを書き、従うことを検証する。
- agentが使う新しい言い訳を見つけて塞ぎ、再検証することでrefactorする。
- skillの種類(technique、pattern、reference)、ディレクトリ構成、`SKILL.md`の構造、発見されやすいdescriptionの最適化を扱う。
- 個人用のskillは実行環境のskillsディレクトリに置く(Claude Codeでは`~/.claude/skills/`)。
- 必須の前提知識であるテスト駆動開発は`references/test-driven-development.md`に同梱している。このskillからだけ読まれ、通常の実装作業では単独で発動しない。
- そのほかの同梱資料: `anthropic-best-practices.md`、`testing-skills-with-subagents.md`、`persuasion-principles.md`、`CLAUDE_MD_TESTING.md`。

## 依存

- subagent: baselineと遵守確認のシナリオ実行に使う。
- 任意: `scripts/render-graphs.js`は`SKILL.md`内の`dot`図をSVGに描画する。Graphviz(`dot`)が必要。

obra/superpowers v6.4.2の`writing-skills` skillをもとに改変した(MIT License、[LICENSE](LICENSE)を参照)。

手順の詳細は[SKILL.md](SKILL.md)を参照。
