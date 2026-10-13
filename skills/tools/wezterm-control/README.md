# wezterm-control

[日本語](README_ja.md)

Operates wezterm panes, tabs, and windows through `wezterm cli`: split, focus, resize, zoom, close, create and rename tabs and windows, read what a pane shows, and send commands to a pane and verify their output.

It is used only when you name wezterm explicitly. tmux and Herdr operations, requests that do not mention wezterm, and edits to wezterm's own configuration (`wezterm.lua`, keybindings) are out of scope.

## Usage

- "weztermのpaneを分割して"
- "weztermの別paneでコマンドを実行して"

```text
weztermのpaneを右に分割して
weztermの隣のpaneで make build を実行して
```

## Behavior

- Every run starts with `wezterm cli list --format json` to get the window, tab, and pane layout. If it fails (no `wezterm`, wezterm not running, mux server unreachable), the skill reports that and stops.
- Passes an explicit `--pane-id` or `--tab-id` to every command, because omitting the ID targets the pane the agent itself runs in (`WEZTERM_PANE`). Relative targets such as "the pane next to me" are resolved with `get-pane-direction`.
- Performs only the operations requested. It does not close, focus, or re-layout panes you did not ask about.
- Sends only non-destructive commands to other panes without confirmation; it asks first for deletion, force-kill, push, deploy, and similar. `kill-pane` is limited to panes the skill created in the session, and anything else needs confirmation.
- `split-pane` and `spawn` move focus to the new pane, so focus is returned to the original pane afterwards unless you asked for the move.
- Sends commands with `send-text --no-paste` and a trailing newline; otherwise the text is pasted and not executed.
- Reads results with `get-text`, using a negative `--start-line` to reach scrollback. Alternate-screen programs (TUIs, coding agents) leave no scrollback, so their output is read from a file the program writes instead.
- Detects completion of long commands by appending an echoed marker with the exit code (for example `__WEZTERM_DONE_0__`) and polling `get-text`.
- The final report lists the operations performed, the pane and tab IDs created or operated on, and the `get-text` verification when a command was sent.

## Dependencies

- `wezterm` CLI (the verified subcommands are listed in [references/cli_reference.md](references/cli_reference.md))

The full procedure lives in [SKILL.md](SKILL.md).
