from datasets import load_dataset
import re
import json
from datetime import datetime

ds = load_dataset(
    "common-pile/caselaw_access_project_filtered",
    streaming=True
)

train = ds["train"]

# Regex patterns

pattern_decided = re.compile(
    r"Decided\s+([A-Z][a-z]{2,}\.?\s+\d{1,2},\s+\d{4})"
)

pattern_circuit = re.compile(
    r"United States Court of Appeals,.*?\.\s+([A-Z][a-z]{2,}\.?\s+\d{1,2},\s+\d{4})"
)

# Convert "Nov. 14, 1972" → "1972-11-14"
def normalize_date(date_str):
    if not date_str:
        return None

    date_str = date_str.replace(".", "")

    try:
        return datetime.strptime(date_str, "%b %d, %Y").date().isoformat()
    except Exception:
        return None


def extract_date(text):
    m = pattern_decided.search(text)
    if m:
        return normalize_date(m.group(1))

    m = pattern_circuit.search(text)
    if m:
        return normalize_date(m.group(1))

    return None


output_path = "output.jsonl"

count = 0

with open(output_path, "w") as f:
    for row in train:
        text = row["text"]

        date = extract_date(text)

        out = {
            "id": row["id"],
            "metadata": row["metadata"],
            "text": text,
            "date": date,
        }

        f.write(json.dumps(out) + "\n")

        count += 1

        # 🔍 Debug line every 1000 samples
        if count % 1000 == 0:
            print(f"Processed {count} samples")

print("Finished. Total rows:", count)
print("Saved to", output_path)