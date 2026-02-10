import json
import os
import ollama
from tqdm import tqdm

# ======================
# CONFIG
# ======================

INPUT_DIR = "weekly_data"
OUTPUT_DIR = "weekly_summaries"

MODEL_NAME = "qwen2.5"
TEXT_LIMIT = 2000

# create output dir if missing
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================
# SUMMARY PROMPT
# ======================

SYSTEM_PROMPT = """
You summarize legal cases.

Write a clear, neutral 2–3 sentence summary focusing on:
- legal issue
- ruling
- why it matters

No fluff.
No markdown.
Plain text only.
"""

# ======================
# SUMMARIZER
# ======================

def summarize_case(text):

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:TEXT_LIMIT]},
            ],
            options={
                "temperature": 0.3,
                "num_predict": 150,
            },
        )

        return response["message"]["content"].strip()

    except Exception as e:
        print("⚠ Summary failed:", e)
        return "Summary unavailable."

# ======================
# WEEK PROCESSOR
# ======================

def process_week(file_path):

    filename = os.path.basename(file_path)
    out_path = os.path.join(
        OUTPUT_DIR,
        filename.replace(".jsonl", "_top.jsonl"),
    )

    with open(file_path, "r") as fin, open(out_path, "w") as fout:

        for line in tqdm(fin, desc=f"Summarizing {filename}"):

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            score = row.get("importance_score", 0)

            # only top cases
            if score < 4:
                continue

            text = row.get("text", "")

            summary = summarize_case(text)

            out = {
                "importance_score": score,
                "summary": summary,
            }

            fout.write(json.dumps(out) + "\n")

    print(f"✅ Wrote summaries → {out_path}")

# ======================
# RUN
# ======================

if __name__ == "__main__":

    try:
        ollama.list()
    except Exception:
        print("❌ Ollama not running. Start with: ollama serve")
        exit(1)

    print("\nScanning weekly files...\n")

    for fname in sorted(os.listdir(INPUT_DIR)):

        if not fname.endswith(".jsonl"):
            continue

        process_week(os.path.join(INPUT_DIR, fname))

    print("\n🎉 Weekly summaries complete.")
