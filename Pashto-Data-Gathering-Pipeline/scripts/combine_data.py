#!/usr/bin/env python3
"""
Script to combine existing cleaned data with newly gathered and cleaned data
"""
import pandas as pd
import os
from datetime import datetime

# Check if files exist
existing_file = ""
new_file = ""

combined_df = None

if os.path.exists(existing_file) and os.path.exists(new_file):
    print(f"Combining existing data {existing_file} with new data {new_file}")
    existing_df = pd.read_csv(existing_file, encoding='utf-8')
    new_df = pd.read_csv(new_file, encoding='utf-8')
    
    # Align columns if needed
    existing_columns = set(existing_df.columns)
    new_columns = set(new_df.columns)
    
    # For simplicity, we'll use only common columns
    common_columns = list(existing_columns.intersection(new_columns))
    if 'title' in common_columns and 'content' in common_columns:
        print(f"Using common columns: {common_columns}")
        existing_df = existing_df[common_columns]
        new_df = new_df[common_columns]
        
        # Combine and remove any duplicates
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        before_len = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['content'], keep='first')
        print(f"Removed {before_len - len(combined_df)} duplicates from combined dataset")
    else:
        print("Warning: Required columns 'title' and 'content' not found in both datasets")
        combined_df = new_df  # Just use the new data
elif os.path.exists(new_file):
    print(f"No existing cleaned data found. Using only new data {new_file}")
    combined_df = pd.read_csv(new_file, encoding='utf-8')
else:
    print("No data files found to combine!")
    exit(1)

# Save the combined dataset
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"/home/kaliai/ZamAI-Pashto-Data-Processing-Pipeline/combined_data/{timestamp}_combined_pashto_dataset.csv"
combined_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Saved combined dataset ({len(combined_df)} entries) to {output_file}")

# Create a symbolic link or copy to a standard name for easy access
standard_file = "/home/kaliai/ZamAI-Pashto-Data-Processing-Pipeline/combined_data/latest_combined_dataset.csv"
if os.path.exists(standard_file):
    os.remove(standard_file)
os.symlink(output_file, standard_file)
print(f"Created symbolic link to latest dataset at {standard_file}")
