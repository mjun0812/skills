---
name: show-me
description: >-
  会話中の話題を、擬似コード・call tree・component tree・file tree・diff・Mermaidのうち、
  要点が伝わる最小の形式でチャットに図示するSkill。
  ユーザーが「図で見せて」「show meして」「形で示して」「どこが変わるか見せて」のように依頼したら使うこと。
  保存する解説ページの作成 (exhtml, exmd) や、会話のまとめ (chat-note) には使わない。
---

# show-me

## 目的

ユーザーが現在の会話の話題を視覚的に理解できるよう助ける。
前置きを省き、散文は短く保つ。要点が明確になる最小の表示を選ぶ。

成果物はチャット本文のtextブロックである。ファイルは作らない。
保存して読み返す解説が必要なら `exhtml` または `exmd` skillに委ねる。

## 形式

- ロジックやアルゴリズムは擬似コードで示す:

  ```text
  on(save)
    if content is unchanged
      return cached result
    write new content
    return fresh result
  ```

- 実行時の制御フローはcall treeで示す:

  ```text
  submitForm
    createSession
      persistPrompt
      launchAgent
    navigateToSession
  ```

- UI構造はcomponent treeで示す。重要な状態やモジュール境界も含める:

  ```tsx
  <SessionPage> (apps/example/src/routes/session.tsx)
    useSessionEvents()
    <SessionToolbar>
      <RunSkillButton> (packages/ui)
  ```

- ファイルの責務や広範なリファクタは浅いfile treeで示す:

  ```text
  src/
  ├── commands/       # ユーザー操作を解釈する
  ├── sessions/       # セッション状態を所有する
  └── transport/      # APIリクエストを送る
  ```

- コンポーネント間の相互作用、制御フロー、データフローはMermaidで示す:

  ```mermaid
  sequenceDiagram
      participant User
      participant UI
      participant Daemon
      User->>UI: choose command
      UI->>Daemon: send expanded prompt
      Daemon-->>UI: stream result
  ```

- 要点が「何が変わるか」であり、周囲の形が既に存在するときは `diff` を使う。diffの形は話題に合わせる。

  コンポーネントの変更なら:

  ```diff
   <SessionPage>
     useSessionEvents()
     <SessionToolbar>
  +    <RunSkillButton />
     <SessionTimeline>
  +    <SkillResultCard />
  ```

  ファイル配置の変更なら:

  ```diff
   src/
   ├── commands/
  +│   └── show-me.ts       # slash commandを展開する
   ├── sessions/
  -└── transport.ts
  +└── transport/
  +    ├── client.ts
  +    └── stream.ts
  ```

  call treeやcall stackの変更なら:

  ```diff
   submitForm
     createSession
       persistPrompt
  +    expandSkillMention
       launchAgent
  -  navigateToSession
  +  navigateToSession
  +    subscribeToEvents
  ```

  状態や制御フローの変更なら:

  ```diff
   on(save)
  -  write content
  +  if content is unchanged
  +    return cached result
  +  write new content
  +  invalidate cache
  ```

- 大部分が新規のとき、文脈を省くと所有関係や順序が見えなくなるとき、またはユーザーがコピーして使える目標の形を必要とするときは、ブロック全体を示す:

  ```ts
  function expandSkill(command: string): string {
    const skillName = command.slice(1);
    return `use the ${skillName} skill`;
  }
  ```

- 視覚的なUI、レイアウト、状態の比較など、Mermaidでは密度が足りない題材は、このSkillでは扱わない。`exhtml` skillでHTMLを作ることをユーザーに提案する。

## 指針

- 各図は、それが補足する短い文の隣に置く。
- ユーザーの現在の質問に答えるため、または現在の論点を解決する選択肢を示すために必要な呼び出し、ファイル、prop、状態、境界だけを残す。
- 形式は1つで足りることが多く、複数使うこともあるが、全部を使うことはまずない。ユーザーを圧倒しない。
