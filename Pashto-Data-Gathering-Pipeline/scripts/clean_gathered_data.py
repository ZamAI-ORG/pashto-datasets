#!/usr/bin/env python3
"""
Script to clean the gathered Pashto text data
"""
import pandas as pd
import glob
import os
import sys
from datetime import datetime

# Import text processing functions directly
from extract_pashto_from_pdf import normalize_text as normalize_pashto_text, preprocess_text as preprocessing

# Directories (will be replaced at runtime)
GATHERED_DIR = "$GATHERED_DIR"
CLEANED_DIR = "$CLEANED_DIR"

# Find the most recent gathered data file
gathered_files = glob.glob(os.path.join(GATHERED_DIR, "*_all_gathered_articles.csv"))
if not gathered_files:
    print("No gathered data files found!")
    sys.exit(1)

gathered_files.sort(key=os.path.getmtime, reverse=True)
latest_file = gathered_files[0]
print(f"Processing latest gathered data: {latest_file}")

df = pd.read_csv(latest_file, encoding='utf-8')
print(f"Loaded {len(df)} articles")

print("Cleaning and normalizing...")
df['cleaned_title'] = df['title'].apply(normalize_pashto_text)
df['cleaned_content'] = df['content'].apply(normalize_pashto_text)

before_len = len(df)
df = df[df['cleaned_content'].str.strip() != ""]
print(f"Removed {before_len - len(df)} entries with empty content")

before_len = len(df)
df = df.drop_duplicates(subset=['cleaned_content'], keep='first')
print(f"Removed {before_len - len(df)} duplicate entries")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.join(CLEANED_DIR, f"{timestamp}_cleaned_gathered_data.csv")
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Saved cleaned data to {output_file}")

jsonl_file = os.path.join(CLEANED_DIR, f"{timestamp}_cleaned_gathered_data.jsonl")
with open(jsonl_file, 'w', encoding='utf-8') as f:
    for _, row in df.iterrows():
        f.write(
            '{"prompt": "' + row['cleaned_title'].replace('"', '\\"') \
            + '", "completion": "' + row['cleaned_content'].replace('"', '\\"') + '"}\n')
print(f"Saved JSONL format for model fine-tuning to {jsonl_file}")
