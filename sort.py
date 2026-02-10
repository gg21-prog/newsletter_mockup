import json
from datetime import datetime
from collections import defaultdict
import os

INPUT = "output_truncated.jsonl"
OUT_DIR = "weekly_data"

os.makedirs(OUT_DIR, exist_ok=True)

files = {}

with open(INPUT, "r") as f:
    for line in f:
        row = json.loads(line)

        if not row["date"]:
            continue

        dt = datetime.fromisoformat(row["date"])
        year, week, _ = dt.isocalendar()

        fname = f"{OUT_DIR}/{year}_week_{week}.jsonl"

        if fname not in files:
            files[fname] = open(fname, "a")

        files[fname].write(line)

# close files
for fh in files.values():
    fh.close()

print("Done — weekly files created")
