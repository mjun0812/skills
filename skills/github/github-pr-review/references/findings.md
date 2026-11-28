# 確定指摘の書き方と findings.json

校正した確定指摘は1つのJSONに書き出し、`scripts/render_review.py`がチャット用の全文レポート(`report.md`)、inline comments(`comments.json`)、GitHubへ投稿するreview本文(`body.md`)を生成する。並び順、連番、項目名の表記、フッターはscriptが付けるので、ここには内容だけを書く。

## 文書の項目

| 項目       | 型        | 内容                                                                                  |
| ---------- | --------- | ------------------------------------------------------------------------------------- |
| `language` | `ja`/`en` | 出力言語。`render_review.py --pr-text` がPRのタイトルと本文から決めた値をそのまま書く |
| `reviewer` | string    | 実行中のレビュワー名。Claude Codeでは `Claude`                                        |
| `model`    | string    | 実行中のmodelの名前。system promptにある表記をそのまま書く。フッターに入る            |
| `commit`   | string    | レビュー対象の `<latest-commit-sha>`。フッターには先頭7文字が入る                     |
| `summary`  | string    | PRの変更内容だけを1〜2文で書く。レビュー結果や指摘件数は書かない                      |
| `notes`    | string[]  | 任意。CIが失敗している場合に1行追加する                                               |
| `findings` | finding[] | 確定指摘。0件なら空配列                                                               |

## 指摘の項目

| 項目                    | 型                          | 内容                                                                                                                                                                                            |
| ----------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `origin`                | `finder`/`claim`            | 由来                                                                                                                                                                                            |
| `proof`                 | `reproduced`/`traced`       | verifierの `証明`。`再現` は `reproduced`、`追跡` は `traced`。scriptは `reproduced` を要修正事項、`traced` を未証明の指摘として、この順に並べて1から連番を付ける。`claim` は `reproduced` だけ |
| `reproduction`          | {command, output}           | `reproduced` で必須。verifierの `実行結果` から、実行用コピーのrootでそのまま動くコマンド列と、問題を示す出力を書く                                                                             |
| `path`, `line`, `side`  | string, int, `RIGHT`/`LEFT` | 指摘の場所。`side` は省略時 `RIGHT`。削除行など変更前ファイル側だけ `LEFT`                                                                                                                      |
| `category`              | string                      | 問題の主な実害を表す1〜3語。処理状態、広すぎる観点、原因や仕組み、重要度、確度は使わない                                                                                                        |
| `summary`               | string                      | 実害だけを1文で書く。原因は `problem` に書く                                                                                                                                                    |
| `problem`               | string                      | 由来ごとの書き方は次節                                                                                                                                                                          |
| `execution_path`        | string[]                    | `finder` で必須。Finderの `証拠` から作る。起点を `path:line`、終点を実害が現れる場所とする最大3ホップで、1要素1ホップを `file:line (説明)` の形で書く                                          |
| `basis`                 | string[]                    | `claim` で必須。PR本文の該当記述の引用                                                                                                                                                          |
| `other_locations`       | string[]                    | 任意。同じ問題を持つ他の `file:line`                                                                                                                                                            |
| `notes`                 | string[]                    | 任意。変更前や踏襲元との比較など、核心ではないが判断に役立つ事実                                                                                                                                |
| `completion_conditions` | (string \| {text, note})[]  | 1件以上。実装方法ではなく、解消を判断できる状態を1条件1文で書く。補足が必要な条件だけ `{"text": ..., "note": ...}` にする。`note`は条件の次の行に出る                                           |

## 内容の規則

- 人間が一読で問題を理解できる平易で自然な表現にし、必要な技術概念だけを一般的な言葉で説明する。推測、修正案、実装方法を追加せず、検証過程は出力しない
- `finder` の `problem` は、発生条件、原因、具体的な実害をこの順で3文以内の1段落に書く。必要な前提とコード上の名称を残し、検証過程、証拠の列挙、重複を除く
- `claim` の `problem` は、PR本文が述べていることと、実行して観察した結果との食い違いをこの順で書く
- `reproduction` の `output` は、問題を示す行だけに絞る。長いログをそのまま貼らない
- `other_locations` と `notes` に分けた内容は `problem` に残さない
- Finderとverifierの生の `証拠` と検証ログは書かない。到達経路は `execution_path` として校正した形で書く

## 例

```json
{
  "language": "ja",
  "reviewer": "Claude",
  "model": "Opus 5.5",
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "summary": "session refresh を logout と独立した非同期処理に分離する。",
  "notes": ["CI: `test (unit)` が失敗している"],
  "findings": [
    {
      "origin": "finder",
      "proof": "reproduced",
      "reproduction": {
        "command": "npx vitest run test/auth/logout-refresh-race.test.ts",
        "output": "AssertionError: expected session to be undefined, received { userId: 'u1' }"
      },
      "path": "src/auth/session.ts",
      "line": 142,
      "category": "セッション残留",
      "summary": "logout 後も古い session が有効なまま残る",
      "problem": "logout と refresh が同時に走ると、refresh が logout 後に完了して古い session を書き戻す。書き戻された session はそのまま有効なので、利用者は logout したつもりで認証済みのままになる。",
      "execution_path": [
        "src/auth/session.ts:142 (refresh が await 後に session を上書き)",
        "src/auth/session.ts:88 (logout は session を削除するが refresh を待たない)",
        "src/api/me.ts:20 (残った session で認証が通る)"
      ],
      "completion_conditions": [
        "logout 後に完了した refresh が session を書き戻さない",
        {
          "text": "logout と refresh の同時実行を再現するテストがある",
          "note": "順序を固定するために fake timer を使ってよい"
        }
      ]
    },
    {
      "origin": "claim",
      "proof": "reproduced",
      "reproduction": {
        "command": "npx vitest run test/auth/logout.test.ts -t 'other devices'",
        "output": "AssertionError: expected 0 sessions for user u1, received 1"
      },
      "path": "src/auth/session.ts",
      "line": 60,
      "category": "検証結果の不一致",
      "summary": "logout 後も他端末の session が残り、PR本文の検証結果と合わない",
      "problem": "PR本文は、logout で同じ利用者の全端末の session が失効することを確かめたと述べている。同じテストを実行すると、他端末の session が1件残る。",
      "basis": [
        "検証「logout で全端末の session が失効する | `npx vitest run test/auth/logout.test.ts` | 通過」"
      ],
      "completion_conditions": ["PR本文の検証結果と、同じ方法を実行した結果が一致する"]
    }
  ]
}
```
