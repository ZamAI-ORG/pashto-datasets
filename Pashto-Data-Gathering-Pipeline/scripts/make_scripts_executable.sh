#!/bin/bash
# Script to make all scripts executable in the Pashto text dataset project
# Created on: June 23, 2025

# Determine script and workspace directories dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Making scripts executable in the Pashto Text Dataset project"
echo "========================================="

# Make all Python and Shell scripts in the scripts directory executable
echo "Making scripts in $SCRIPT_DIR executable..."
find "$SCRIPT_DIR" -type f \( -name "*.py" -o -name "*.sh" \) | while read file; do
    if [ -f "$file" ]; then
        chmod +x "$file"
        echo "Made executable: $(basename "$file")"
    fi
done

# Optional: also make any top-level scripts executable
echo -e "\nChecking for scripts in workspace root..."
find "$WORKSPACE_DIR" -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" \) | while read file; do
    chmod +x "$file" && echo "Made executable: $(basename "$file")"
done

# Verify scripts are executable
echo -e "\nVerifying executable permissions:"
echo "-----------------------------------------"
find "$SCRIPT_DIR" -type f \( -name "*.py" -o -name "*.sh" \) | while read file; do
    if [ -x "$file" ]; then
        echo "✓ $(basename "$file")"
    else
        echo "✗ $(basename "$file") (Failed to make executable)"
    fi
done

echo "========================================="
echo "Script execution completed!"
echo "All Python and Shell scripts should now be executable."
echo "========================================="

# Provide helpful information about running the scripts
echo -e "\nTo run the full data processing pipeline:"
echo "  cd $SCRIPT_DIR && ./gather_clean_combine.sh"
echo
echo "To extract text from PDF files:"
echo "  cd $SCRIPT_DIR && ./extract_pdf_text.sh"
echo
echo "To run data cleaning only:"
echo "  cd $SCRIPT_DIR && ./run_data_cleaning.sh"
echo "========================================="
