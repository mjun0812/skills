#!/usr/bin/env python
"""Collect one user's pull request, issue, and review activity under an owner.

Usage:
    collect_activity.py --owner <owner> --since <YYYY-MM-DD> --until <YYYY-MM-DD>
                        [--user <login>] [--tz <IANA name>]

Both ends of the range are inclusive dates in the time zone given by --tz
(default: the local one), and every timestamp in the output is converted to
that zone. --user defaults to the login authenticated with gh.

Prints a JSON document to stdout. items holds the pull requests and issues the
user acted on within the range, plus open pull requests still waiting for the
user's review. excluded holds the ones the user is involved in but did nothing
to within the range. state is each item's state at the end of the range and
current_state its state now; review_pending is as of now. warnings names each
search that matched more items than the API returns.
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

# In these timeline events the actor is the mentioned or subscribed user, or
# the one whose merge made GitHub delete the head branch, not someone acting.
IGNORED_EVENTS = {"mentioned", "subscribed", "unsubscribed", "head_ref_deleted"}


def gh_json(*args: str) -> Any:  # noqa: ANN401
    """Run gh and parse its stdout as JSON.

    Args:
        *args: Arguments passed to gh.

    Returns:
        The parsed JSON value.
    """
    result = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def search(query: str) -> tuple[list[dict[str, Any]], int]:
    """Return the pull requests and issues that match a search query.

    The search API returns at most 1,000 items per query.

    Args:
        query: A GitHub issue search query.

    Returns:
        The items read, and the total number of matches.
    """
    pages = gh_json(
        "api",
        "-X",
        "GET",
        "search/issues",
        "-f",
        f"q={query}",
        "-f",
        "per_page=100",
        "--paginate",
        "--slurp",
    )
    return [item for page in pages for item in page["items"]], pages[0]["total_count"]


def timeline(repo: str, number: int) -> list[dict[str, Any]]:
    """Return the timeline events of a pull request or issue.

    Args:
        repo: The repository as owner/name.
        number: The pull request or issue number.

    Returns:
        The timeline events, oldest first.
    """
    pages = gh_json(
        "api",
        f"repos/{repo}/issues/{number}/timeline?per_page=100",
        "--paginate",
        "--slurp",
    )
    return [event for page in pages for event in page]


def localize(timestamp: str | None, tz: tzinfo) -> str | None:
    """Convert an ISO 8601 timestamp from the API to the report's time zone.

    Args:
        timestamp: The timestamp, or None.
        tz: The report's time zone.

    Returns:
        The converted timestamp with its UTC offset, or None.
    """
    if timestamp is None:
        return None
    return datetime.fromisoformat(timestamp).astimezone(tz).isoformat()


def actions_of(
    item: dict[str, Any],
    events: list[dict[str, Any]],
    user: str,
    start: datetime,
    end: datetime,
) -> list[dict[str, str]]:
    """Pick the user's actions on one item within [start, end).

    Args:
        item: The search item.
        events: The item's timeline events.
        user: The login whose actions are picked.
        start: The inclusive start of the range.
        end: The exclusive end of the range.

    Returns:
        The actions, oldest first, each with an event name and a UTC timestamp.
    """
    found = []
    if item["user"]["login"] == user:
        found.append({"event": "opened", "at": item["created_at"]})
    for event in events:
        name = event.get("event")
        actor = event.get("actor") or event.get("user") or {}
        at = event.get("created_at") or event.get("submitted_at")
        if name in IGNORED_EVENTS or actor.get("login") != user or at is None:
            continue
        action = {"event": name, "at": at}
        if name == "reviewed":
            action["state"] = event["state"]
        elif name in ("labeled", "unlabeled"):
            action["label"] = event["label"]["name"]
        elif name in ("assigned", "unassigned"):
            action["assignee"] = event["assignee"]["login"]
        elif name in ("review_requested", "review_request_removed"):
            reviewer = event.get("requested_reviewer") or event.get("requested_team")
            action["reviewer"] = reviewer.get("login") or reviewer["name"]
        found.append(action)
    in_range = [a for a in found if start <= datetime.fromisoformat(a["at"]) < end]
    return sorted(in_range, key=lambda a: datetime.fromisoformat(a["at"]))


def summarize(item: dict[str, Any]) -> dict[str, Any]:
    """Describe a search item with the fields the report needs.

    Args:
        item: The search item.

    Returns:
        The item's repository, number, kind, title, URL, and author.
    """
    return {
        "repo": item["repository_url"].split("/repos/", 1)[1],
        "number": item["number"],
        "kind": "pr" if "pull_request" in item else "issue",
        "title": item["title"],
        "url": item["html_url"],
        "author": item["user"]["login"],
    }


def main() -> None:
    """Collect the activity and print it as JSON."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--owner", required=True)
    parser.add_argument("--since", required=True, type=date.fromisoformat)
    parser.add_argument("--until", required=True, type=date.fromisoformat)
    parser.add_argument("--user")
    parser.add_argument("--tz", type=ZoneInfo)
    args = parser.parse_args()

    tz = args.tz or datetime.now().astimezone().tzinfo
    start = datetime.combine(args.since, time(), tz)
    end = datetime.combine(args.until + timedelta(days=1), time(), tz)
    try:
        user = args.user or gh_json("api", "user")["login"]
        since = start.astimezone(UTC).isoformat()
        until = (end - timedelta(seconds=1)).astimezone(UTC).isoformat()
        queries = {
            "involved": f"user:{args.owner} involves:{user} updated:>={since}",
            "reviewed": f"user:{args.owner} is:pr reviewed-by:{user} updated:>={since}",
            "pending": f"user:{args.owner} is:pr is:open review-requested:{user} updated:>={since}",
            "closed": f"user:{args.owner} closed:{since}..{until}",
        }
        results = {key: search(query) for key, query in queries.items()}
        found = {key: items for key, (items, _) in results.items()}
        warnings = [
            f"{queries[key]}: read {len(items)} of {total} matches; split the range"
            for key, (items, total) in results.items()
            if total > len(items)
        ]
        candidates = {item["url"]: item for items in found.values() for item in items}
        with ThreadPoolExecutor(max_workers=8) as pool:
            events = dict(
                zip(
                    candidates,
                    pool.map(
                        lambda item: timeline(summarize(item)["repo"], item["number"]),
                        candidates.values(),
                    ),
                    strict=True,
                )
            )
    except subprocess.CalledProcessError as e:
        sys.exit(f"gh {' '.join(e.cmd[1:])} failed:\n{e.stderr}")

    pending = {item["url"] for item in found["pending"]}
    involved = {item["url"] for item in found["involved"] + found["reviewed"]}
    items, excluded = [], []
    for url, item in candidates.items():
        actions = actions_of(item, events[url], user, start, end)
        if not actions and url not in pending:
            if url in involved:
                excluded.append(summarize(item))
            continue
        merged_at = (item.get("pull_request") or {}).get("merged_at")

        def by_end(timestamp: str | None) -> bool:
            return timestamp is not None and datetime.fromisoformat(timestamp) < end

        items.append(
            {
                **summarize(item),
                "author_is_bot": item["user"]["type"] == "Bot",
                "state": "merged"
                if by_end(merged_at)
                else "closed"
                if by_end(item["closed_at"])
                else "open",
                "current_state": "merged" if merged_at else item["state"],
                "draft": item.get("draft", False),
                "created_at": localize(item["created_at"], tz),
                "closed_at": localize(item["closed_at"], tz),
                "merged_at": localize(merged_at, tz),
                "review_pending": url in pending,
                "actions": [{**a, "at": localize(a["at"], tz)} for a in actions],
            }
        )

    def order(record: dict[str, Any]) -> tuple[str, int]:
        return record["repo"], record["number"]

    json.dump(
        {
            "owner": args.owner,
            "user": user,
            "since": args.since.isoformat(),
            "until": args.until.isoformat(),
            "timezone": str(tz),
            "queries": list(queries.values()),
            "warnings": warnings,
            "items": sorted(items, key=order),
            "excluded": sorted(excluded, key=order),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
