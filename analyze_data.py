import argparse
import csv
import re
from datetime import datetime

csv.field_size_limit(10**9)

POSITIVE_REACTIONS = ["+1", "laugh", "hooray", "heart", "rocket"]
NEGATIVE_REACTIONS = ["-1", "confused", "eyes"]

POSITIVE_TERMS = [
    "helpful",
    "clear",
    "great docs",
    "well documented",
    "well written",
    "thanks for the docs",
    "easy to follow",
    "nice example",
    "much better",
    "love the",
    "very useful",
]

NEGATIVE_TERMS = [
    "no documentation",
    "undocumented",
    "not documented",
    "missing",
    "lacks",
    "nothing explains",
    "no example",
    "outdated",
    "out of date",
    "obsolete",
    "deprecated",
    "wrong",
    "incorrect",
    "no longer works",
    "doesn't match",
    "confusing",
    "unclear",
    "hard to understand",
    "ambiguous",
    "misleading",
    "vague",
    "doesn't explain",
    "couldn't find",
    "hard to find",
    "where is",
    "buried",
    "not obvious",
    "broken link",
    "404",
    "spent hours",
    "spent days",
    "struggled",
    "frustrating",
    "painful",
    "gave up",
]

COLUMNS = [
    "number",
    "record_type",
    "status",
    "time_open",
    "num_assignees",
    "num_comments",
    "total_reactions",
    "positive_reactions",
    "negative_reactions",
    "positive_buzzwords",
    "negative_buzzwords",
]


def buildPattern(terms):
    ordered = sorted(terms, key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(t) for t in ordered) + r")(?!\w)", re.IGNORECASE)


POSITIVE_PATTERN = buildPattern(POSITIVE_TERMS)
NEGATIVE_PATTERN = buildPattern(NEGATIVE_TERMS)


def parseTime(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None


def countWords(text):
    text = text.replace("’", "'")
    return len(POSITIVE_PATTERN.findall(text)), len(NEGATIVE_PATTERN.findall(text))


def countReactions(row):
    positive = sum(int(row[f"react_{k}"] or 0) for k in POSITIVE_REACTIONS)
    negative = sum(int(row[f"react_{k}"] or 0) for k in NEGATIVE_REACTIONS)
    return int(row["react_total"] or 0), positive, negative


def timeOpen(row):
    if row["state"] != "closed":
        return ""
    end = parseTime(row["merged_at"]) if row["record_type"] == "pr" and row["merged_at"] else parseTime(row["closed_at"])
    if not end:
        return ""
    return formatTimespan(end - parseTime(row["created_at"]))


def formatTimespan(span):
    return round(span.total_seconds() / 86400, 2)


def readComments(comments):
    stats = {}
    total = 0

    print(f"Reading PR comments from {comments} ")

    with open(comments, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(line.replace("\0", "") for line in file)
        for row in reader:
            total += 1
            pr = stats.setdefault(row["pr_number"].strip(), {
                "num_comments": 0,
                "total_reactions": 0,
                "positive_reactions": 0,
                "negative_reactions": 0,
                "positive_buzzwords": 0,
                "negative_buzzwords": 0,
            })
            reactTotal, reactPositive, reactNegative = countReactions(row)
            wordsPositive, wordsNegative = countWords(row["body"])
            pr["num_comments"] += 1
            pr["total_reactions"] += reactTotal
            pr["positive_reactions"] += reactPositive
            pr["negative_reactions"] += reactNegative
            pr["positive_buzzwords"] += wordsPositive
            pr["negative_buzzwords"] += wordsNegative

    print(f"Read {total} comments on {len(stats)} PR's")
    return stats


def buildRecords(data, commentStats):
    records = []
    counts = {"issue": 0, "pr": 0}

    print(f"Building records from {data} ")

    with open(data, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            counts[row["record_type"]] += 1
            reactTotal, reactPositive, reactNegative = countReactions(row)
            wordsPositive, wordsNegative = countWords(f"{row['title']}\n{row['body']}")
            record = {
                "number": row["number"],
                "record_type": row["record_type"],
                "status": row["state"],
                "time_open": timeOpen(row),
                "num_assignees": len([a for a in row["assignees"].split(";") if a.strip()]),
                "num_comments": int(row["num_comments"] or 0),
                "total_reactions": reactTotal,
                "positive_reactions": reactPositive,
                "negative_reactions": reactNegative,
                "positive_buzzwords": wordsPositive,
                "negative_buzzwords": wordsNegative,
            }
            if row["record_type"] == "pr":
                pr = commentStats.get(row["number"].strip(), {})
                record["num_comments"] = pr.get("num_comments", 0)
                for key in ["total_reactions", "positive_reactions", "negative_reactions",
                            "positive_buzzwords", "negative_buzzwords"]:
                    record[key] += pr.get(key, 0)
            records.append(record)

    print(f"Built {counts['issue']} issue records, {counts['pr']} PR records")
    return records


def writeOutput(records, out):
    with open(out, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record)
        print(f"Successfully wrote {len(records)} records to {out}")


def main():
    ap = argparse.ArgumentParser(description="Build one analysis record per zephyr issue + pr, combining PR comment data.")
    ap.add_argument("--data", default="filtered_data.csv", help="Name of filtered issues + prs input file, should end in .csv")
    ap.add_argument("--comments", default="filtered_comments.csv", help="Name of filtered PR comments input file, should end in .csv")
    ap.add_argument("--out", default="analysis_dataset.csv", help="Name of output file, should end in .csv")
    a = ap.parse_args()

    commentStats = readComments(a.comments)
    records = buildRecords(a.data, commentStats)
    writeOutput(records, a.out)


if __name__ == "__main__":
    main()