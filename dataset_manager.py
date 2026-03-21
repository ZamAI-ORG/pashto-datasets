import os
import shutil
import json
import csv
from typing import List, Dict, Any, Tuple


# ---------------------------------------------------------------------------
# File-level helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Dataset validation
# ---------------------------------------------------------------------------

def validate_dataset(file_path: str) -> Tuple[bool, List[str]]:
    """Validate a JSONL dataset file for common quality issues.

    Checks performed:
    - Every record has non-empty ``instruction`` and ``response`` fields.
    - No duplicate instructions.
    - ``instruction`` and ``response`` are strings.

    Returns a tuple ``(is_valid, issues)`` where *is_valid* is ``True`` only
    when the issues list is empty.
    """
    issues: List[str] = []

    if not os.path.exists(file_path):
        return False, [f"File not found: {file_path}"]

    records: List[Dict[str, Any]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(f"Line {line_no}: JSON parse error – {exc}")
                continue

            if not isinstance(record.get("instruction"), str) or not record["instruction"].strip():
                issues.append(f"Line {line_no}: missing or empty 'instruction'")
            if not isinstance(record.get("response"), str) or not record["response"].strip():
                issues.append(f"Line {line_no}: missing or empty 'response'")

            records.append(record)

    # Duplicate check (instruction + input together form the unique key)
    seen: dict = {}
    for idx, record in enumerate(records, start=1):
        # For summarisation-style examples the "input" field carries the article
        # text; two records with the same instruction but different inputs are
        # distinct, so we key on both.
        key = (
            record.get("instruction", "").strip(),
            record.get("input", "").strip(),
        )
        if key in seen:
            issues.append(
                f"Duplicate entry at record {idx} (first seen at record {seen[key]}): "
                f"instruction='{key[0][:60]}...'"
            )
        else:
            seen[key] = idx

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Dataset statistics
# ---------------------------------------------------------------------------

def get_dataset_stats(file_path: str) -> Dict[str, Any]:
    """Return summary statistics for a JSONL dataset file.

    Returns a dict with keys:
    - ``total``: total number of records
    - ``categories``: dict mapping category → count
    - ``avg_instruction_len``: average character length of instructions
    - ``avg_response_len``: average character length of responses
    """
    stats: Dict[str, Any] = {
        "total": 0,
        "categories": {},
        "avg_instruction_len": 0.0,
        "avg_response_len": 0.0,
    }

    if not os.path.exists(file_path):
        return stats

    instruction_lens: List[int] = []
    response_lens: List[int] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            stats["total"] += 1
            cat = record.get("category", "unknown")
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
            instruction_lens.append(len(record.get("instruction", "")))
            response_lens.append(len(record.get("response", "")))

    if instruction_lens:
        stats["avg_instruction_len"] = round(sum(instruction_lens) / len(instruction_lens), 1)
    if response_lens:
        stats["avg_response_len"] = round(sum(response_lens) / len(response_lens), 1)

    return stats


# ---------------------------------------------------------------------------
# __main__ – demo / smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    default_dataset = "zamai_final_dataset/zamai_training_dataset.jsonl"
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else default_dataset

    if not os.path.exists(dataset_path):
        print(f"Dataset not found at '{dataset_path}'.")
        print("Run 'python create_dataset_simple.py' first to generate a dataset.")
        sys.exit(1)

    print(f"📊 Dataset statistics for: {dataset_path}")
    stats = get_dataset_stats(dataset_path)
    print(f"  Total records        : {stats['total']}")
    print(f"  Avg instruction len  : {stats['avg_instruction_len']} chars")
    print(f"  Avg response len     : {stats['avg_response_len']} chars")
    print("  Categories:")
    for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1]):
        print(f"    {cat:<25} {count}")

    print()
    print(f"🔍 Validating: {dataset_path}")
    is_valid, issues = validate_dataset(dataset_path)
    if is_valid:
        print("  ✅ No issues found.")
    else:
        print(f"  ❌ {len(issues)} issue(s) found:")
        for issue in issues[:20]:
            print(f"    - {issue}")
        if len(issues) > 20:
            print(f"    ... and {len(issues) - 20} more.")

