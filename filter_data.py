import argparse
import csv
import mine_raw_data

csv.field_size_limit(10**9)

def readInput(data):
    counts = {"issue": 0, "pr": 0, "issue_f": 0, "pr_f": 0}
    filteredList = []
    
    print(f"Filtering issues and PR's from {data} ")
    
    with open(data, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            counts[row["record_type"]] += 1
            labels = [l.strip() for l in row["labels"].split(";")]
            if "area: Documentation" in labels:
                counts[row["record_type"] + "_f"] += 1
                filteredList.append(row)
    
    print(f"Total records filtered: {counts['issue']} issues, {counts['pr']} PR's")
    print(f"Remaining filtered records: {counts['issue_f']} issues, {counts['pr_f']} PR's")
    
    return filteredList
    
def writeOutput(filteredList, out):
    with open(out, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, mine_raw_data.COLUMNS)
        writer.writeheader()
        for row in filteredList:
            writer.writerow(row)
        print(f"Successfully wrote filtered records to {out}")   

def main():
    ap = argparse.ArgumentParser(description="Retrieve raw zephyr issues + prs to one CSV.")
    ap.add_argument("--data", default="official_raw_data.csv", help="Name of input file, should end in .csv")
    ap.add_argument("--out", default="filtered_data.csv", help="Name of output file, should end in .csv")
    a = ap.parse_args()
    
    filteredList = readInput(a.data)
    writeOutput(filteredList, a.out)     
    
if __name__ == "__main__":
    main()