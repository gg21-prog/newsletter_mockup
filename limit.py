INPUT = "output.jsonl"
OUTPUT = "output_truncated.jsonl"

TARGET_GB = 5
TARGET_BYTES = TARGET_GB * 1024**3

bytes_written = 0
lines = 0

with open(INPUT, "rb") as src, open(OUTPUT, "wb") as dst:
    for line in src:
        line_size = len(line)

        if bytes_written + line_size > TARGET_BYTES:
            break

        dst.write(line)
        bytes_written += line_size
        lines += 1

        if lines % 100000 == 0:
            print(
                f"Lines: {lines} | Size: {bytes_written / 1024**3:.2f} GB"
            )

print("\nDone!")
print("Lines kept:", lines)
print(f"Final size: {bytes_written / 1024**3:.2f} GB")
print("Saved as:", OUTPUT)
