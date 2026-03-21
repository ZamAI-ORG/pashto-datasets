#!/usr/bin/env python3
"""
Unit tests for ZamAI Pashto dataset utilities.

Run with:  pytest tests/
"""

import csv
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Make sure the repo root is on the path so imports work regardless of how
# pytest is invoked.
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dataset_manager import (
    get_dataset_stats,
    insert_csv,
    insert_json,
    insert_jsonl,
    validate_dataset,
)
from create_dataset_simple import (
    STANDARD_CATEGORIES,
    _normalize_category,
    create_simple_dataset,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_jsonl(path: Path, records: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Tests: category normalisation
# ---------------------------------------------------------------------------

class TestNormalizeCategory:
    def test_legacy_geography_maps_to_tutor_chat(self):
        assert _normalize_category("geography") == "tutor_chat"

    def test_legacy_health_maps_to_general_qa(self):
        assert _normalize_category("health") == "general_qa"

    def test_legacy_islamic_maps_to_islamic_content(self):
        assert _normalize_category("islamic") == "islamic_content"

    def test_legacy_culture_maps_to_cultural_content(self):
        assert _normalize_category("culture") == "cultural_content"

    def test_legacy_business_maps_to_business_automation(self):
        assert _normalize_category("business") == "business_automation"

    def test_legacy_summarization_maps_to_news_summarization(self):
        assert _normalize_category("summarization") == "news_summarization"

    def test_canonical_name_passes_through(self):
        for cat in STANDARD_CATEGORIES:
            assert _normalize_category(cat) == cat

    def test_unknown_category_passes_through(self):
        assert _normalize_category("custom_domain") == "custom_domain"


# ---------------------------------------------------------------------------
# Tests: create_simple_dataset
# ---------------------------------------------------------------------------

class TestCreateSimpleDataset:
    def test_creates_jsonl_file(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        assert (out / "zamai_training_dataset.jsonl").exists()

    def test_creates_json_file(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        assert (out / "zamai_training_dataset.json").exists()

    def test_creates_csv_file(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        assert (out / "zamai_training_dataset.csv").exists()

    def test_creates_dataset_info(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        info_path = out / "dataset_info.json"
        assert info_path.exists()
        info = json.loads(info_path.read_text(encoding="utf-8"))
        assert "total_examples" in info
        assert info["total_examples"] > 0

    def test_all_records_have_canonical_categories(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        with open(out / "zamai_training_dataset.jsonl", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                cat = rec.get("category", "")
                assert cat in STANDARD_CATEGORIES, f"Non-standard category: {cat}"

    def test_all_records_have_instruction_and_response(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        with open(out / "zamai_training_dataset.jsonl", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                assert rec.get("instruction", "").strip(), "Empty instruction found"
                assert rec.get("response", "").strip(), "Empty response found"

    def test_csv_has_correct_row_count(self, tmp_path):
        out = create_simple_dataset(str(tmp_path))
        info = json.loads((out / "dataset_info.json").read_text(encoding="utf-8"))
        total = info["total_examples"]
        with open(out / "zamai_training_dataset.csv", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == total


# ---------------------------------------------------------------------------
# Tests: validate_dataset
# ---------------------------------------------------------------------------

class TestValidateDataset:
    def test_valid_dataset_returns_no_issues(self, tmp_path):
        p = tmp_path / "good.jsonl"
        _write_jsonl(p, [
            {"instruction": "پوښتنه یوه", "response": "ځواب یوه", "category": "tutor_chat"},
            {"instruction": "پوښتنه دوه", "response": "ځواب دوه", "category": "general_qa"},
        ])
        ok, issues = validate_dataset(str(p))
        assert ok
        assert issues == []

    def test_missing_instruction_is_flagged(self, tmp_path):
        p = tmp_path / "bad.jsonl"
        _write_jsonl(p, [{"response": "ځواب"}])
        ok, issues = validate_dataset(str(p))
        assert not ok
        assert any("instruction" in i for i in issues)

    def test_empty_response_is_flagged(self, tmp_path):
        p = tmp_path / "bad.jsonl"
        _write_jsonl(p, [{"instruction": "پوښتنه", "response": "   "}])
        ok, issues = validate_dataset(str(p))
        assert not ok
        assert any("response" in i for i in issues)

    def test_duplicate_instructions_are_flagged(self, tmp_path):
        p = tmp_path / "dup.jsonl"
        _write_jsonl(p, [
            {"instruction": "same", "response": "a"},
            {"instruction": "same", "response": "b"},
        ])
        ok, issues = validate_dataset(str(p))
        assert not ok
        assert any("Duplicate" in i for i in issues)

    def test_same_instruction_different_input_not_flagged(self, tmp_path):
        """Summarisation examples share a generic instruction but have distinct inputs."""
        p = tmp_path / "summ.jsonl"
        _write_jsonl(p, [
            {"instruction": "دا متن لنډ کړه:", "input": "text one", "response": "a"},
            {"instruction": "دا متن لنډ کړه:", "input": "text two", "response": "b"},
        ])
        ok, issues = validate_dataset(str(p))
        assert ok, f"Expected valid but got: {issues}"

    def test_missing_file_returns_error(self, tmp_path):
        ok, issues = validate_dataset(str(tmp_path / "nonexistent.jsonl"))
        assert not ok
        assert any("not found" in i for i in issues)


# ---------------------------------------------------------------------------
# Tests: get_dataset_stats
# ---------------------------------------------------------------------------

class TestGetDatasetStats:
    def test_returns_correct_total(self, tmp_path):
        p = tmp_path / "data.jsonl"
        _write_jsonl(p, [
            {"instruction": "q1", "response": "a1", "category": "tutor_chat"},
            {"instruction": "q2", "response": "a2", "category": "general_qa"},
            {"instruction": "q3", "response": "a3", "category": "tutor_chat"},
        ])
        stats = get_dataset_stats(str(p))
        assert stats["total"] == 3

    def test_category_counts_are_correct(self, tmp_path):
        p = tmp_path / "data.jsonl"
        _write_jsonl(p, [
            {"instruction": "q1", "response": "a1", "category": "tutor_chat"},
            {"instruction": "q2", "response": "a2", "category": "tutor_chat"},
            {"instruction": "q3", "response": "a3", "category": "islamic_content"},
        ])
        stats = get_dataset_stats(str(p))
        assert stats["categories"]["tutor_chat"] == 2
        assert stats["categories"]["islamic_content"] == 1

    def test_missing_file_returns_empty_stats(self, tmp_path):
        stats = get_dataset_stats(str(tmp_path / "none.jsonl"))
        assert stats["total"] == 0

    def test_avg_lengths_are_positive(self, tmp_path):
        p = tmp_path / "data.jsonl"
        _write_jsonl(p, [
            {"instruction": "short q", "response": "short a"},
        ])
        stats = get_dataset_stats(str(p))
        assert stats["avg_instruction_len"] > 0
        assert stats["avg_response_len"] > 0


# ---------------------------------------------------------------------------
# Tests: insert helpers
# ---------------------------------------------------------------------------

class TestInsertHelpers:
    def test_insert_jsonl_appends_records(self, tmp_path):
        p = tmp_path / "data.jsonl"
        insert_jsonl(str(p), [{"instruction": "q", "response": "a"}])
        insert_jsonl(str(p), [{"instruction": "q2", "response": "a2"}])
        with open(p, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) == 2

    def test_insert_json_creates_and_extends(self, tmp_path):
        p = tmp_path / "data.json"
        insert_json(str(p), [{"x": 1}])
        insert_json(str(p), [{"x": 2}])
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_insert_csv_creates_with_header(self, tmp_path):
        p = tmp_path / "data.csv"
        insert_csv(str(p), [{"col1": "v1", "col2": "v2"}])
        with open(p, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert rows[0]["col1"] == "v1"
