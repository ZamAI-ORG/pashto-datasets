#!/bin/bash

# This script runs the Comprehensive Data Cleaning notebook to clean the Pashto text dataset
# It will create a cleaned_data directory with the processed files ready for model fine-tuning


echo "Starting Pashto dataset cleaning process..."

# Set correct notebook and output paths
NOTEBOOK_PATH="/workspaces/Pashto-Dataset-Creating-Dataset/Pashto-Data-Gathering-Pipeline/scripts/Comprehensive_Data_Cleaning.ipynb"
OUTPUT_PATH="/workspaces/Pashto-Dataset-Creating-Dataset/Pashto-Data-Gathering-Pipeline/scripts/Comprehensive_Data_Cleaning_executed.ipynb"
CLEANED_DATA_DIR="/workspaces/Pashto-Dataset-Creating-Dataset/cleaned_data"

jupyter nbconvert --to notebook --execute "$NOTEBOOK_PATH" --output "$OUTPUT_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Data cleaning completed successfully!"
    echo "Cleaned data is available in the $CLEANED_DATA_DIR directory."
else
    echo "❌ Error occurred during data cleaning. Please check the notebook for details."
fi

if combined_df.empty or combined_df.columns.size == 0:
    print("DataFrame is empty or has no columns. Check your data loading and preprocessing steps.")
else:
    print(combined_df.describe(include='all'))

