# Legal Case Newsletter Pipeline

## Project Overview

This project is a prototype pipeline that simulates how weekly legal case data could be processed and curated into a newsletter-style digest.

The system uses the Caselaw Access Project dataset from Hugging Face and demonstrates how large-scale textual data can be ingested, structured, evaluated using an open-source LLM, and transformed into readable summaries.

Dataset source: [https://huggingface.co/datasets/common-pile/caselaw_access_project_filtered](https://huggingface.co/datasets/common-pile/caselaw_access_project_filtered), demonstrating how real-time weekly legal data could be filtered and transformed into digestible insights.

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.8+
- [Ollama](https://github.com/jmorganca/ollama) with a compatible model (the scripts use `qwen2.5`)
- Required Python packages (install via pip):
  - `datasets`
  - `ollama`
  - `tqdm`

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install required Python packages:
   ```bash
   pip install datasets ollama tqdm
   ```

3. Download and install Ollama from [https://github.com/jmorganca/ollama](https://github.com/jmorganca/ollama)

4. Pull the required model:
   ```bash
   ollama pull qwen2.5
   ```

## How to Run the Pipeline

The pipeline consists of five main scripts that should be run in sequence:

### 1. Data Filtering (`filtering.py`)
This script downloads and filters the legal case dataset from Hugging Face.

**Purpose**: Extracts relevant legal cases from the Caselaw Access Project dataset, extracts dates from the text, and saves the data in JSONL format.

**Run the script**:
```bash
python filtering.py
```

**Output**: Creates `output.jsonl` with filtered legal cases containing IDs, metadata, text, and extracted dates.

### 2. Data Truncation (`limit.py`)
This script limits the dataset size to handle large datasets more efficiently.

**Purpose**: Truncates the full dataset to a specified size (5GB by default) to prevent memory issues and reduce processing time during development and testing.

**Run the script**:
```bash
python limit.py
```

**Input**: Expects `output.jsonl` from the filtering step
**Output**: Creates `output_truncated.jsonl` with a subset of the original data

### 3. Data Sorting (`sort.py`)
This script organizes the filtered/truncated data by week.

**Purpose**: Groups legal cases by week of the year and creates separate files for each week to enable weekly processing.

**Run the script**:
```bash
python sort.py
```

**Input**: Expects `output_truncated.jsonl` (or `output.jsonl` - adjust the INPUT variable in the script if needed)
**Output**: Creates weekly files in the `weekly_data/` directory named as `{year}_week_{week}.jsonl`

### 3. Scoring (`scoring_ollama_qwen.py`)
This script assigns importance scores to each legal case using an LLM.

**Purpose**: Uses an open-source LLM (Qwen2.5) to evaluate and score each legal case from 1-5 based on legal importance (1 = trivial/local, 3 = moderate precedent, 5 = landmark case).

**Run the script**:
```bash
# First, start Ollama server in a separate terminal
ollama serve

# Then run the scoring script in another terminal
python scoring_ollama_qwen.py
```

**Output**: Adds an `importance_score` field to each entry in the weekly data files.

### 4. Summarization (`filter_summarize.py`)
This script generates summaries for the most important legal cases.

**Purpose**: Filters cases with high importance scores (≥4) and generates concise summaries using an LLM, creating a newsletter-ready format.

**Run the script**:
```bash
# Make sure Ollama server is running
ollama serve

# Then run the summarization script
python filter_summarize.py
```

**Output**: Creates summary files in the `weekly_summaries/` directory with the format `{original_filename}_top.jsonl`

## Script Descriptions

### `filtering.py`
- Downloads the Caselaw Access Project dataset from Hugging Face
- Extracts dates from legal texts using regex patterns
- Outputs structured data with case text, metadata, and normalized dates

### `limit.py`
- Limits the dataset size to handle large datasets more efficiently
- Truncates the full dataset to a specified size (5GB by default)
- Prevents memory issues and reduces processing time during development and testing

### `sort.py`
- Organizes cases by week using ISO calendar weeks
- Creates separate files for each week to enable batch processing
- Prepares data for time-based analysis

### `scoring_ollama_qwen.py`
- Evaluates legal case importance using an LLM
- Processes cases in batches for efficiency
- Assigns scores from 1-5 based on legal significance
- Handles errors gracefully with fallback scoring

### `filter_summarize.py`
- Filters for high-importance cases (score ≥4)
- Generates concise summaries focusing on legal issue, ruling, and significance
- Outputs clean, readable summaries suitable for newsletters

## Directory Structure

Note: The `weekly_data/` and `weekly_summaries/` directories will automatically be created when the respective scripts are run.

```
.
├── filtering.py          # Download and filter dataset
├── limit.py             # Truncate dataset to manageable size
├── sort.py              # Organize cases by week
├── scoring_ollama_qwen.py # Score case importance
├── filter_summarize.py  # Generate summaries
├── README.md           # This file
├── weekly_data/        # Weekly organized case files (created automatically)
└── weekly_summaries/   # Generated summaries (created automatically)
```

## Customization

You can customize the following aspects of the pipeline:

- **Model**: Change the `MODEL_NAME` variable in the scripts to use a different Ollama model
- **Importance Threshold**: Modify the score threshold (currently 4) in `filter_summarize.py` to include more or fewer cases
- **Text Limit**: Adjust `TEXT_LIMIT` to control how much text is sent to the LLM
- **Batch Size**: Modify `BATCH_SIZE` in `scoring_ollama_qwen.py` to change processing batch sizes

## Notes

- The pipeline assumes Ollama is running locally when executing scoring and summarization scripts
- Large datasets may take considerable time to process, especially with LLM-based scoring and summarization
- The regex patterns in `filtering.py` are tuned for extracting dates from legal documents and may need adjustment for different document formats