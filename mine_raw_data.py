import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:
    sys.exit("Missing dependency 'requests', run pip install requests")

OWNER, REPO = "zephyrproject-rtos", "zephyr"
API = "https://api.github.com"
DEFAULT_START = "2021-01-01"
DEFAULT_END = "2026-01-01"

REACTION_KEYS = [
    "+1", 
    "-1", 
    "laugh", 
    "hooray", 
    "confused", 
    "heart", 
    "rocket", 
    "eyes"]

COLUMNS = [
    "record_type",       
    "number",
    "title",
    "body",                 
    "labels",               
    "state",                
    "state_reason",
    "is_draft",
    "author",
    "author_type",
    "author_association",
    "assignees",
    "milestone",
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at",
    "num_comments",
    "locked",
    *[f"react_{k}" for k in REACTION_KEYS],
    "react_total",
    "html_url",
]


def make_session():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN environment variable not set, correct this and try again")
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return session


def wait_for_reset(response):
    if "Retry-After" in response.headers:
        delay = int(response.headers["Retry-After"])
    else:
        reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        delay = max(reset - time.time(), 0) + 5
    print(f"  rate limit reached, sleeping {int(delay)}s ...", flush=True)
    time.sleep(delay)


def get(session, url, params=None):
    for attempt in range(5):
        try:
            response = session.get(url, params=params, timeout=90)
        except requests.RequestException as e:
            print(f"  network error ({e}), retrying ...", flush=True)
            time.sleep(min(2 ** attempt, 60))
            continue
        if response.status_code == 200:
            if int(response.headers.get("X-RateLimit-Remaining", 1)) < 3:
                wait_for_reset(response)
            return response
        if response.status_code in (403, 429) and (
            response.headers.get("X-RateLimit-Remaining") == "0"
            or "Retry-After" in response.headers
            or "rate limit" in response.text.lower()
        ):
            wait_for_reset(response)
            continue
        if response.status_code >= 500:
            time.sleep(min(2 ** attempt, 60))
            continue
        sys.exit(f"GitHub returned {response.status_code}: {response.text[:300]}")
    sys.exit(f"Gave up after repeated failures on {url}")


def parse_time(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None


def to_row(item):
    is_pr = "pull_request" in item
    user = item.get("user") or {}
    rx = item.get("reactions") or {}
    return {
        "record_type": "pr" if is_pr else "issue",
        "number": item["number"],
        "title": item.get("title") or "",
        "body": (item.get("body") or "").replace("\r\n", "\n"),
        "labels": ";".join(l["name"] for l in item.get("labels", [])),
        "state": item.get("state"),
        "state_reason": item.get("state_reason") or "",
        "is_draft": item.get("draft", "") if is_pr else "",
        "author": user.get("login", ""),
        "author_type": user.get("type", ""),
        "author_association": item.get("author_association", ""),
        "assignees": ";".join(a["login"] for a in item.get("assignees") or []),
        "milestone": (item.get("milestone") or {}).get("title", ""),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "closed_at": item.get("closed_at") or "",
        "merged_at": ((item.get("pull_request") or {}).get("merged_at") or "") if is_pr else "",
        "num_comments": item.get("comments", 0),
        "locked": item.get("locked", False),
        **{f"react_{k}": rx.get(k, 0) for k in REACTION_KEYS},
        "react_total": rx.get("total_count", 0),
        "html_url": item.get("html_url"),
    }


def main():
    ap = argparse.ArgumentParser(description="Retrieve raw zephyr issues + prs to one CSV.")
    ap.add_argument("--start", default=DEFAULT_START, help="Starting timestamp, inclusive (YYYY-MM-DD, UTC)")
    ap.add_argument("--end", default=DEFAULT_END, help="Ending timestamp, exclusive (YYYY-MM-DD, UTC)")
    ap.add_argument("--out", default="raw_data.csv", help="Name of output file, should end in .csv")
    ap.add_argument("--max-records", type=int, default=0, help="stop after N rows (testing)")
    a = ap.parse_args()

    start = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(a.end).replace(tzinfo=timezone.utc)
    session = make_session()
    partial = a.out + ".partial"

    url = f"{API}/repos/{OWNER}/{REPO}/issues"
    params = {"state": "all", "sort": "created", "direction": "desc", "per_page": 100}

    seen = set()
    counts = {"issue": 0, "pr": 0}
    page = 0
    print(f"Retrieving issues and PRs created {start:%Y-%m-%d} to {end:%Y-%m-%d} (UTC) ...")

    with open(partial, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        done = False
        while url and not done:
            r = get(session, url, params)
            items = r.json()
            page += 1
            oldest = None
            for item in items:
                created = parse_time(item["created_at"])
                oldest = created
                if created >= end:
                    continue
                if created < start:
                    done = True
                    break
                if item["number"] in seen:
                    continue
                seen.add(item["number"])
                row = to_row(item)
                writer.writerow(row)
                counts[row["record_type"]] += 1
                if a.max_records and len(seen) >= a.max_records:
                    done = True
                    break
            f.flush()
            if oldest:
                print(f"  page {page}: {counts['issue']} issues, {counts['pr']} PRs "
                      f"(reached {oldest:%Y-%m-%d})", flush=True)
            url = r.links.get("next", {}).get("url")
            params = None

    os.replace(partial, a.out)
    print(f"Done: {counts['issue']} issues + {counts['pr']} PRs = "
          f"{counts['issue'] + counts['pr']} rows -> {a.out}")


if __name__ == "__main__":
    main()