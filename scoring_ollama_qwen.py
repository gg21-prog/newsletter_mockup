import json
import os
import ollama
from tqdm import tqdm

# ======================
# CONFIG
# ======================

WEEKLY_DIR = "weekly_data"

BATCH_SIZE = 6
TEXT_LIMIT = 2000
MODEL_NAME = "qwen2.5"

START_FILE = "1973_week_19.jsonl"

# ======================
# PROMPT
# ======================

SYSTEM_INSTRUCTION = """
You are a legal analyst API. You strictly output structured data.

Task: Score each case from 1–5 by legal importance.
1 = trivial/local
3 = moderate precedent
5 = landmark case

Output rules:
- EXACTLY one line per case
- Format: <case number>: <score>
- No commentary
- No markdown
- No extra text

Example:
1: 3
2: 5
3: 1
"""

# ======================
# BATCH SCORING
# ======================

def batch_score(texts):

    cases_text = "\n\n".join(
        f"Case {i+1}:\n{text[:TEXT_LIMIT]}"
        for i, text in enumerate(texts)
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": cases_text},
            ],
            options={
                "temperature": 0.1,
                "num_predict": 100,
            },
        )

        raw_text = response["message"]["content"]

        print("\n=== RAW MODEL OUTPUT ===")
        print(raw_text)
        print("========================\n")

        raw_lines = raw_text.strip().split("\n")
        scores = []

        for line in raw_lines:

            if ":" not in line:
                continue

            try:
                left, right = line.split(":", 1)

                idx = left.lower().replace("case", "").strip()

                if not idx.isdigit():
                    continue

                token = right.strip().split()[0]
                token = token.replace(".", "").replace(",", "")

                score = int(token)

                if 1 <= score <= 5:
                    scores.append(score)

            except Exception as e:
                print("Parse warn:", line, e)

        print("Parsed scores:", scores)

        while len(scores) < len(texts):
            print("⚠ Padding missing score → default 3")
            scores.append(3)

        return scores[:len(texts)]

    except Exception as e:
        print("⚠ Ollama failure → fallback batch:", e)
        return [3] * len(texts)

# ======================
# FILE PROCESSOR
# ======================

def process_file(path):

    tmp = path + ".tmp"

    with open(path, "r") as fin, open(tmp, "w") as fout:

        batch_rows = []
        batch_texts = []

        for line in tqdm(fin, desc=os.path.basename(path)):

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if "importance_score" in row:
                fout.write(json.dumps(row) + "\n")
                continue

            text = row.get("text", "")

            batch_rows.append(row)
            batch_texts.append(text)

            if len(batch_rows) == BATCH_SIZE:

                scores = batch_score(batch_texts)

                for r, s in zip(batch_rows, scores):
                    r["importance_score"] = s
                    fout.write(json.dumps(r) + "\n")

                batch_rows = []
                batch_texts = []

        if batch_rows:

            scores = batch_score(batch_texts)

            for r, s in zip(batch_rows, scores):
                r["importance_score"] = s
                fout.write(json.dumps(r) + "\n")

    os.replace(tmp, path)

# ======================
# RUN — MULTI FILE
# ======================

if __name__ == "__main__":

    try:
        ollama.list()
    except Exception:
        print("❌ Ollama not running. Start with: ollama serve")
        exit(1)

    print("\nScanning weekly_data folder...\n")

    START = False
    for filename in sorted(os.listdir(WEEKLY_DIR)):
        if not filename.endswith(".jsonl"):
            continue
        if filename == START_FILE:
            START = True
        
        if START:
            path = os.path.join(WEEKLY_DIR, filename)

            print(f"\n🚀 Processing: {filename}")
            process_file(path)

    print("\n✅ All files scored.")
