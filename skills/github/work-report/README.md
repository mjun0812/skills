# work-report

[日本語](README_ja.md)

Turn the work a user did in a period into a report on a single HTML page. The period is a day, a week, a month, or a quarter. It defaults to a week. The material is the pull requests, issues, and reviews under a GitHub owner (an org or a user), plus conversations with Claude Code and Codex.

The page has four sections: Pull Request, Issue, Review, and Work with agents. Pull requests are grouped by repository and theme, and each row carries one sentence of background. The same change made in several repositories becomes one row, and bot dependency updates take one row per repository. Each conversation becomes a row per session that sums up what was done.

Scripts do the collection and the rendering, and the agent writes only the grouping and the wording of each row, so every report looks the same.

## Usage

- 「今週の作業を報告書にして」
- 「先月の作業をまとめて」
- 「日報を作って」
- 「四半期の振り返りを作って」

## Arguments

| Argument        | Effect                                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| owner           | The org or user to report on. Asked for when neither the request nor the cwd's git remote decides it                                    |
| user            | The user whose work is reported. Defaults to the user authenticated with gh                                                             |
| period          | Today, yesterday, this or last week, this or last month, a quarter, or start and end dates. Defaults to the last 7 days including today |
| time zone       | The time zone for the range boundaries and the dates shown. Defaults to the local one                                                   |
| subject name    | The name used in the page title. Defaults to the owner name                                                                             |
| previous report | The URL or file of the previous report. When given, merged, closed, and opened items it already lists are left out                      |

Weeks start on Monday, and quarters follow the calendar year (Q1 is January to March). A request can name other boundaries.

## Behavior

- `scripts/collect_activity.py` searches the owner for pull requests and issues that match any of these:
  - the user is involved (author, assignee, mentioned, commenter)
  - the user reviewed them
  - a review request to the user is still pending
  - they were closed within the range
- It picks the user's actions within the range (opening, merging, reviewing, assigning) from each item's timeline. Items without any are dropped, and every timestamp is converted to the given time zone.
- When a search hits the API limit of 1,000 items, it warns, and the agent collects again over shorter ranges.
- `scripts/collect_sessions.py` collects the Claude Code and Codex sessions in which the user typed a prompt within the range. The logs live in `${CLAUDE_CONFIG_DIR:-~/.claude}/projects` and `${CODEX_HOME:-~/.codex}/sessions`. Subagent threads and non-interactive Codex runs are skipped, and every other session counts, whatever its repository.
- The agent sorts the items and sessions into sections and groups, writes each row from the pull request and issue bodies and from the session prompts and replies, and saves the report JSON. Conversations are summed up and never quoted. Secrets, credentials, personal information, and working directory paths are left out.
- `scripts/render_report.py` validates the report JSON and renders the HTML with a fixed layout and style. Violations are reported one per line, so the agent fixes the JSON and runs it again.
- When a tool can publish HTML as a page (such as Claude Code's Artifact tool), the page is published as a new one; otherwise the HTML path is reported. The previous report's page is never overwritten.
- Direct pushes that skip pull requests, and actions on items the user is not involved in (such as labeling someone else's issue), are not collected. Row states are as of the end of the range, and pending reviews are as of the run.

## Dependencies

- `gh` CLI, authenticated
- `python3` (3.11 or later, standard library only)
- `git`, to find the repository of a Claude Code session's working directory
- `jq` and `mktemp`, to read the collected JSON and create the work directory
- macOS or Linux

The full procedure lives in [SKILL.md](SKILL.md).
