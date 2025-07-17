import os
import shutil
import json
import csv
from typing import List

def copy_dataset_files(source_folder: str, target_folder: str, file_types: List[str] = ["json", "jsonl", "csv"]):
    """
    Copy all dataset files of specified types from source_folder to target_folder.
    Creates target_folder if it does not exist.
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    for file_name in os.listdir(source_folder):
        if any(file_name.endswith(ext) for ext in file_types):
            src = os.path.join(source_folder, file_name)
            dst = os.path.join(target_folder, file_name)
            shutil.copy2(src, dst)
            print(f"Copied {file_name} to {target_folder}")


def insert_jsonl(file_path: str, new_data: List[dict]):
    """
    Insert new data (list of dicts) into a JSONL file.
    """
    with open(file_path, "a", encoding="utf-8") as f:
        for item in new_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Inserted {len(new_data)} records into {file_path}")


def insert_json(file_path: str, new_data: List[dict]):
    """
    Insert new data (list of dicts) into a JSON file (as an array).
    """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            data.extend(new_data)
        else:
            data = new_data
    else:
        data = new_data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Inserted {len(new_data)} records into {file_path}")


def insert_csv(file_path: str, new_data: List[dict]):
    """
    Insert new data (list of dicts) into a CSV file.
    """
    fieldnames = new_data[0].keys() if new_data else []
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for item in new_data:
            writer.writerow(item)
    print(f"Inserted {len(new_data)} records into {file_path}")


if __name__ == "__main__":
    # Example usage:
    # Copy all dataset files from a session folder to zamai_final_dataset
    # Example: Copy files from zamai_final_dataset to another folder (for demonstration)
    # copy_dataset_files("zamai_final_dataset", "zamai_final_dataset_backup")
    print("No source folder found. Update the path in copy_dataset_files() to a valid folder if you want to copy datasets.")

    # Insert new records into a JSONL file
    # new_records = [{"instruction": "...", "response": "...", "category": "..."}]
    # insert_jsonl("zamai_final_dataset/zamai_training_dataset.jsonl", new_records)

    # Insert new records into a JSON file
    # insert_json("zamai_final_dataset/zamai_training_dataset.json", new_records)

    # Insert new records into a CSV file
    # insert_csv("zamai_final_dataset/zamai_training_dataset.csv", new_records)
