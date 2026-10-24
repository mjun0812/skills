#!/usr/bin/env python
"""Collect the Claude Code and Codex sessions the user prompted in a date range.

Usage:
    collect_sessions.py --since <YYYY-MM-DD> --until <YYYY-MM-DD> [--tz <IANA name>]

Reads the session logs under ${CLAUDE_CONFIG_DIR:-~/.claude}/projects and
${CODEX_HOME:-~/.codex}/sessions (and archived_sessions). A session is collected when the user typed
at least one prompt within the range. Subagent threads and non-interactive
Codex runs are skipped, because the session that started them covers their
work. Both ends of the range are inclusive dates in the time zone given by
--tz (default: the local one).

Prints a JSON document to stdout with one entry per session, oldest first.
Prompts and replies are truncated, and every timestamp is converted to the
report's time zone. warnings names each log that had replies but no prompt
the script could recognize.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from datetime import date, datetime, time, timedelta, tzinfo
from functools import cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROMPTS_KEPT = 3
PROMPT_CHARS = 300
REPLY_CHARS = 500
# Any host, so GitHub Enterprise Server URLs and remotes match too.
GITHUB_REF = re.compile(r"https://[\w.-]+/[\w.-]+/[\w.-]+/(?:pull|issues)/\d+")
GITHUB_REMOTE = re.compile(r"[\w.-]+[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$")
# Codex sends AGENTS.md and environment context as user messages.
CODEX_INJECTED = ("<", "# AGENTS.md instructions")


class Session:
    """The parts of one session log that fall within the range."""

    def __init__(self, agent: str, path: Path) -> None:
        """Start an empty session.

        Args:
            agent: ``claude-code`` or ``codex``.
            path: The session log file.
        """
        self.agent = agent
        self.path = path
        self.id = path.stem
        self.cwd: str | None = None
        self.repo: str | None = None
        self.title: str | None = None
        self.prompts: list[tuple[datetime, str]] = []
        self.last_reply: str | None = None
        self.last_at: datetime | None = None
        self.refs: set[str] = set()

    def reply(self, at: datetime, text: str) -> None:
        """Record an assistant reply.

        Args:
            at: When the reply was written.
            text: The reply text.
        """
        self.last_reply = text
        self.last_at = at
        self.refs.update(GITHUB_REF.findall(text))

    def to_json(self, tz: tzinfo) -> dict[str, Any]:
        """Describe the session for the report.

        Args:
            tz: The report's time zone.

        Returns:
            The session's identity, place, title, prompts, and last reply.
        """
        times = [at for at, _ in self.prompts] + [self.last_at or self.prompts[0][0]]
        return {
            "agent": self.agent,
            "id": self.id,
            "path": str(self.path),
            "cwd": self.cwd,
            "repo": self.repo,
            "title": self.title,
            "started_at": min(times).astimezone(tz).isoformat(),
            "ended_at": max(times).astimezone(tz).isoformat(),
            "prompt_count": len(self.prompts),
            "prompts": [
                shorten(t, PROMPT_CHARS) for _, t in self.prompts[:PROMPTS_KEPT]
            ],
            "last_reply": self.last_reply and shorten(self.last_reply, REPLY_CHARS),
            "github_refs": sorted(self.refs),
        }


def shorten(text: str, limit: int) -> str:
    """Collapse whitespace and cut text to a length.

    Args:
        text: The text to shorten.
        limit: The maximum number of characters kept.

    Returns:
        The shortened text, ending with an ellipsis when it was cut.
    """
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit] + "…"


def records(path: Path) -> Iterator[dict[str, Any]]:
    """Yield the JSON records of a session log, skipping unreadable lines.

    Args:
        path: The session log file.
    """
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def text_of(content: object, types: tuple[str, ...]) -> str:
    """Join the text blocks of a message content.

    Args:
        content: A string, or a list of content blocks.
        types: The block types that carry text.

    Returns:
        The joined text.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        b.get("text", "")
        for b in content
        if isinstance(b, dict) and b.get("type") in types
    )


@cache
def github_repo(cwd: str) -> str | None:
    """Return the owner/name of the GitHub origin of a working directory.

    Args:
        cwd: The session's working directory.

    Returns:
        The repository, or None when the directory is gone or not on GitHub.
    """
    if not Path(cwd).is_dir():
        return None
    result = subprocess.run(
        ["git", "-C", cwd, "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
    )
    match = GITHUB_REMOTE.search(result.stdout.strip())
    return match.group(1) if match else None


def claude_session(path: Path, start: datetime, end: datetime) -> Session:
    """Read one Claude Code session log.

    Args:
        path: The session log file.
        start: The inclusive start of the range.
        end: The exclusive end of the range.

    Returns:
        The session, with prompts and replies limited to the range.
    """
    session = Session("claude-code", path)
    for rec in records(path):
        kind = rec.get("type")
        if kind == "ai-title":
            session.title = rec.get("aiTitle")
            continue
        if kind not in ("user", "assistant") or "timestamp" not in rec:
            continue
        at = datetime.fromisoformat(rec["timestamp"])
        if not start <= at < end:
            continue
        session.cwd = rec.get("cwd") or session.cwd
        content = rec.get("message", {}).get("content")
        if kind == "user" and (rec.get("origin") or {}).get("kind") == "human":
            session.prompts.append((at, text_of(content, ("text",))))
        elif kind == "assistant" and (text := text_of(content, ("text",))):
            session.reply(at, text)
    if session.cwd:
        session.repo = github_repo(session.cwd)
    return session


def codex_session(
    path: Path, start: datetime, end: datetime, titles: dict[str, str]
) -> Session | None:
    """Read one Codex session log.

    Args:
        path: The session log file.
        start: The inclusive start of the range.
        end: The exclusive end of the range.
        titles: Thread names by session ID.

    Returns:
        The session, or None for a subagent thread or a non-interactive run.
    """
    session = Session("codex", path)
    for rec in records(path):
        payload = rec.get("payload") or {}
        if rec.get("type") == "session_meta" and session.cwd is None:
            source = payload.get("source")
            if (
                payload.get("thread_source") == "subagent"
                or (isinstance(source, dict) and "subagent" in source)
                or payload.get("originator") == "codex_exec"
            ):
                return None
            session.id = payload.get("id", session.id)
            session.cwd = payload.get("cwd")
            url = (payload.get("git") or {}).get("repository_url") or ""
            match = GITHUB_REMOTE.search(url)
            session.repo = match.group(1) if match else None
            continue
        if (
            rec.get("type") != "response_item"
            or payload.get("type") != "message"
            or "timestamp" not in rec
        ):
            continue
        at = datetime.fromisoformat(rec["timestamp"])
        if not start <= at < end:
            continue
        text = text_of(payload.get("content"), ("input_text", "output_text"))
        if payload.get("role") == "user" and not text.startswith(CODEX_INJECTED):
            session.prompts.append((at, text))
        elif payload.get("role") == "assistant" and text:
            session.reply(at, text)
    session.title = titles.get(session.id)
    return session


def codex_titles(codex_home: Path) -> dict[str, str]:
    """Read the thread names Codex keeps for its sessions.

    Args:
        codex_home: The Codex home directory.

    Returns:
        The latest thread name by session ID.
    """
    index = codex_home / "session_index.jsonl"
    if not index.exists():
        return {}
    return {
        rec["id"]: rec["thread_name"]
        for rec in records(index)
        if rec.get("id") and rec.get("thread_name")
    }


def main() -> None:
    """Collect the sessions and print them as JSON."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--since", required=True, type=date.fromisoformat)
    parser.add_argument("--until", required=True, type=date.fromisoformat)
    parser.add_argument("--tz", type=ZoneInfo)
    args = parser.parse_args()

    tz = args.tz or datetime.now().astimezone().tzinfo
    start = datetime.combine(args.since, time(), tz)
    end = datetime.combine(args.until + timedelta(days=1), time(), tz)
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))

    def recent(paths: Iterator[Path]) -> list[Path]:
        return [p for p in paths if p.stat().st_mtime >= start.timestamp()]

    # Subagent transcripts live in subdirectories, so only top-level logs match.
    sessions: list[Session | None] = [
        claude_session(p, start, end)
        for p in recent((claude_home / "projects").glob("*/*.jsonl"))
    ]
    titles = codex_titles(codex_home)
    sessions += [
        codex_session(p, start, end, titles)
        for directory in ("sessions", "archived_sessions")
        for p in recent((codex_home / directory).glob("**/*.jsonl"))
    ]
    found = sorted(
        (s for s in sessions if s and s.prompts), key=lambda s: s.prompts[0][0]
    )
    # Replies without any prompt mean the log format changed and prompts were missed.
    unreadable = [str(s.path) for s in sessions if s and s.last_reply and not s.prompts]
    json.dump(
        {
            "since": args.since.isoformat(),
            "until": args.until.isoformat(),
            "timezone": str(tz),
            "sessions": [s.to_json(tz) for s in found],
            "warnings": [
                f"{path}: replies but no prompts found; check the log format"
                for path in unreadable
            ],
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
