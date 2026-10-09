import argparse
import csv
import mine_raw_data

csv.field_size_limit(10**9)

DOC_LABEL = "area: Documentation"


def readInput(data):
    counts = {"issue": 0, "pr": 0, "issue_f": 0, "pr_f": 0}
    filteredList = []
    docPrNumbers = set()

    print(f"Filtering issues and PR's from {data} ")

    with open(data, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            counts[row["record_type"]] += 1
            labels = [l.strip() for l in row["labels"].split(";")]
            if DOC_LABEL in labels:
                counts[row["record_type"] + "_f"] += 1
                filteredList.append(row)
                if row["record_type"] == "pr":
                    docPrNumbers.add(row["number"].strip())

    print(f"Total records filtered: {counts['issue']} issues, {counts['pr']} PR's")
    print(f"Remaining filtered records: {counts['issue_f']} issues, {counts['pr_f']} PR's")

    return filteredList, docPrNumbers


def writeOutput(filteredList, out):
    with open(out, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, mine_raw_data.COLUMNS)
        writer.writeheader()
        for row in filteredList:
            writer.writerow(row)
        print(f"Successfully wrote filtered records to {out}")


def filterComments(comments, out, docPrNumbers):
    total = 0
    kept = 0
    bots = 0

    print(f"Filtering PR comments from {comments} ")

    with open(comments, mode="r", newline="", encoding="utf-8") as inFile, \
         open(out, mode="w", newline="", encoding="utf-8") as outFile:
        reader = csv.DictReader(line.replace("\0", "") for line in inFile)
        writer = csv.DictWriter(outFile, reader.fieldnames)
        writer.writeheader()
        for row in reader:
            total += 1
            if row["author_type"].strip() == "Bot":
                bots += 1
                continue
            if row["pr_number"].strip() in docPrNumbers:
                writer.writerow(row)
                kept += 1

    print(f"Total comments filtered: {total} ({bots} bot comments removed)")
    print(f"Remaining filtered comments: {kept} (on {len(docPrNumbers)} documentation PR's)")
    print(f"Successfully wrote filtered comments to {out}")


def main():
    ap = argparse.ArgumentParser(description="Filter zephyr issues, PRs, and PR comments down to the documentation label.")
    ap.add_argument("--data", default="raw_data.csv", help="Name of input file, should end in .csv")
    ap.add_argument("--out", default="filtered_data.csv", help="Name of output file, should end in .csv")
    ap.add_argument("--comments", default="raw_comments.csv", help="Name of PR comments input file, should end in .csv")
    ap.add_argument("--comments-out", default="filtered_comments.csv", help="Name of filtered PR comments output file, should end in .csv")
    a = ap.parse_args()

    filteredList, docPrNumbers = readInput(a.data)
    writeOutput(filteredList, a.out)
    filterComments(a.comments, a.comments_out, docPrNumbers)


if __name__ == "__main__":
    main()