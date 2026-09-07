# tools

## wezterm-control

Operate wezterm panes, tabs, and windows through `wezterm cli`: split, focus, resize, zoom, close, create and rename tabs and windows, read what a pane shows, and send commands to a pane and verify their output. Only used when the user names wezterm explicitly; tmux and other multiplexers are out of scope, as is editing wezterm's own configuration.

Every run starts with `wezterm cli list --format json` and passes an explicit `--pane-id` or `--tab-id` to every command, because omitting the ID targets the pane the agent itself runs in. Only the operations the user asked for are performed, only non-destructive commands are sent to other panes without confirmation, and `kill-pane` is limited to panes the skill created. Focus is returned to the original pane afterwards.

Patterns the skill relies on:

- Send a command with `send-text --no-paste` and a trailing newline, otherwise it is pasted and not executed.
- Read results with `get-text`, using a negative `--start-line` to reach scrollback. Alternate-screen programs (TUIs, coding agents) do not leave scrollback, so their output is read from a file instead.
- Detect completion of long commands by appending an echoed marker with the exit code and polling `get-text`.

- Trigger phrases: "weztermのpaneを分割して", "weztermの別paneでコマンドを実行して".

The verified subcommand list is in `wezterm-control/references/cli_reference.md`; the rules and steps are in `SKILL.md`.
