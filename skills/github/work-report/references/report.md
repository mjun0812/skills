# report JSON

`scripts/render_report.py` の入力。ページの構成と見た目はscriptが決めるため、JSONには表示する内容だけを書く。文字列はすべてページの言語で書く。

## 例

```json
{
  "title": "example 週次作業 10/18–10/24",
  "heading": "example 週次作業 (octocat)",
  "meta": "対象期間: 2026-10-18 (日) 〜 2026-10-24 (土) / example の repo とエージェントとの session",
  "stats": [
    { "value": 3, "label": "PR を merge (うち Bot 1)" },
    { "value": 1, "label": "レビュー待ち" },
    { "value": 2, "label": "エージェントとの session" }
  ],
  "sections": [
    {
      "heading": "Pull Request",
      "groups": [
        {
          "label": "api",
          "theme": "batch の安定化",
          "items": [
            {
              "number": 287,
              "url": "https://github.com/example/api/pull/287",
              "state": "merged",
              "title": "fix: DB への接続のタイムアウトを 60 秒に延ばす",
              "note": "約 12 時間の処理の後、最初の接続が既定の 10 秒でタイムアウトしていた",
              "date": "10/18"
            }
          ]
        },
        {
          "label": "全 repo 共通",
          "theme": "証明書の更新",
          "items": [
            {
              "state": "merged",
              "title": "chore(deps): certifi を 2026.10.19 に上げる",
              "links": [
                { "text": "api#259", "url": "https://github.com/example/api/pull/259" },
                { "text": "web#183", "url": "https://github.com/example/web/pull/183" }
              ],
              "date": "10/22"
            }
          ]
        },
        {
          "label": "Bot",
          "theme": "依存更新の merge",
          "items": [
            {
              "title": "web: cryptography 50.0.1",
              "links": [{ "text": "web#161", "url": "https://github.com/example/web/pull/161" }],
              "date": "10/22"
            }
          ]
        }
      ]
    },
    {
      "heading": "レビュー",
      "groups": [
        {
          "label": "レビュー待ち",
          "theme": "作成者 hubot、未レビュー",
          "items": [
            {
              "number": 273,
              "url": "https://github.com/example/search/pull/273",
              "state": "open",
              "title": "search: feat: 検索 API を新しい index に統一する",
              "date": "10/18"
            }
          ]
        }
      ]
    },
    {
      "heading": "エージェントとの作業",
      "groups": [
        {
          "label": "example/api",
          "items": [
            {
              "tag": "Claude Code",
              "title": "staging の batch が保存に失敗した原因を調べた",
              "note": "長時間の処理の後の再接続がタイムアウトしていると特定し、PR にした",
              "links": [{ "text": "api#287", "url": "https://github.com/example/api/pull/287" }],
              "date": "10/18"
            },
            {
              "tag": "Codex",
              "title": "PR #149 を dry-run でレビューした",
              "date": "10/18"
            }
          ]
        }
      ]
    }
  ],
  "footer": "集計方法: user:example で involves / reviewed-by / review-requested:octocat と期間内の close を検索し、Claude Code と Codex の session ログを読んだ。期間は 2026-10-18〜2026-10-24 (Asia/Tokyo)。"
}
```

## フィールド

| フィールド | 型                 | 必須 | 内容                                                               |
| ---------- | ------------------ | ---- | ------------------------------------------------------------------ |
| `title`    | string             | 必須 | ページの `<title>`。ブラウザのタブと一覧に出る名前                 |
| `heading`  | string             | 必須 | ページ先頭の見出し                                                 |
| `meta`     | string             | 必須 | 見出し直下の1行。対象期間と対象範囲                                |
| `stats`    | `{value, label}[]` | 必須 | 見出し下に並べる件数。`value` は整数。空配列なら件数の行を出さない |
| `sections` | `section[]`        | 必須 | 節の並び。1つ以上                                                  |
| `footer`   | string             | 必須 | ページ末尾の1段落。集計方法と除外したitem                          |
| `lang`     | string             | 任意 | ページの言語 (BCP 47)。既定は `ja`                                 |

`section`:

| フィールド | 型        | 必須 | 内容       |
| ---------- | --------- | ---- | ---------- |
| `heading`  | string    | 必須 | 節の見出し |
| `groups`   | `group[]` | 必須 | 1つ以上    |

`group`:

| フィールド | 型       | 必須 | 内容                                                              |
| ---------- | -------- | ---- | ----------------------------------------------------------------- |
| `label`    | string   | 任意 | 等幅の強調色で出す見出し。repo名や操作の種類                      |
| `theme`    | string   | 任意 | `label` の右に薄く出す補足。作業のテーマ                          |
| `items`    | `item[]` | 必須 | 1つ以上。`label` と `theme` がどちらも無いgroupは見出しなしで出す |

`item` は、番号付きの行 (`number` と `url` を持つ) と、番号なしの行のどちらかになる。番号なしの行は `links` を持てる。1つのgroupに両方を混ぜられない。

| フィールド | 型              | 必須         | 内容                                                                                                         |
| ---------- | --------------- | ------------ | ------------------------------------------------------------------------------------------------------------ |
| `title`    | string          | 必須         | 行の本文                                                                                                     |
| `date`     | string          | 必須         | 右端に出す日付。`MM/DD`、複数日にわたるなら `MM/DD–MM/DD`                                                    |
| `state`    | string          | 任意         | 行頭の色付きpill。`merged` / `open` / `closed` / `draft` / `approved` / `changes_requested`                  |
| `tag`      | string          | 任意         | `state` の後ろに薄く出すpill。会話の行のagent名 (`Claude Code`、`Codex`)                                     |
| `note`     | string          | 任意         | 本文の下に薄く出す1文                                                                                        |
| `number`   | integer         | 番号付きの行 | 左端に `#<number>` として出す                                                                                |
| `url`      | string          | 番号付きの行 | `#<number>` のリンク先                                                                                       |
| `links`    | `{text, url}[]` | 任意         | 番号なしの行の本文の下に並べるリンク。同じ変更を入れた複数のPR、1行にまとめた複数のPR、会話で作ったPR・Issue |
