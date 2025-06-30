#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ZamAI Big Data Archive Processor
Extract and process the large Pashto archives for base model training.
"""

import os
import gzip
import tarfile
import json
import pandas as pd
from pathlib import Path
import re
from typing import List, Dict, Iterator
import sqlite3
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PashtoArchiveProcessor:
    def __init__(self, archive_path: str = "Pashto-Data"):
        """Initialize the archive processor."""
        self.archive_path = Path(archive_path)
        self.output_path = Path("processed_archives")
        self.output_path.mkdir(exist_ok=True)
        
        # Archive locations
        self.archive_locations = [
            self.archive_path / "archives",
            self.archive_path / "Pashto_High_value_dataset"
        ]
        
    def find_archives(self) -> Dict[str, Path]:
        """Find all available archives."""
        archives = {}
        
        for location in self.archive_locations:
            if location.exists():
                for file in location.glob("*.tar.gz"):
                    archives[file.stem] = file
                for file in location.glob("*.gz"):
                    if not file.name.endswith('.tar.gz'):
                        archives[file.stem] = file
        
        logger.info(f"Found {len(archives)} archives: {list(archives.keys())}")
        return archives
    
    def extract_tar_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract tar.gz archive."""
        try:
            logger.info(f"Extracting {archive_path.name}...")
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_to)
            logger.info(f"✅ Extracted {archive_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to extract {archive_path.name}: {e}")
            return False
    
    def extract_gz_file(self, gz_path: Path, extract_to: Path) -> bool:
        """Extract .gz file."""
        try:
            logger.info(f"Extracting {gz_path.name}...")
            output_file = extract_to / gz_path.stem
            
            with gzip.open(gz_path, 'rt', encoding='utf-8') as f_in:
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            
            logger.info(f"✅ Extracted {gz_path.name} to {output_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to extract {gz_path.name}: {e}")
            return False
    
    def process_sql_import(self, sql_file: Path) -> Iterator[Dict]:
        """Process SQL import file and extract data."""
        logger.info(f"Processing SQL file: {sql_file.name}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract INSERT statements
        insert_pattern = r"INSERT INTO.*?VALUES\s*\((.*?)\);"
        matches = re.findall(insert_pattern, content, re.DOTALL)
        
        count = 0
        for match in matches:
            try:
                # Basic parsing of values (simplified)
                values = match.split(',')
                if len(values) >= 2:
                    # Assume structure: id, title, content, ...
                    title = values[1].strip().strip("'\"")
                    content = values[2].strip().strip("'\"") if len(values) > 2 else ""
                    
                    if title and content:
                        yield {
                            'id': count,
                            'title': title,
                            'content': content,
                            'source': sql_file.stem
                        }
                        count += 1
            except Exception as e:
                continue
        
        logger.info(f"Extracted {count} records from {sql_file.name}")
    
    def process_text_corpus(self, text_file: Path) -> Iterator[Dict]:
        """Process plain text corpus file."""
        logger.info(f"Processing text corpus: {text_file.name}")
        
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 50:  # Filter out very short paragraphs
                yield {
                    'id': i,
                    'title': f"Paragraph {i+1}",
                    'content': paragraph,
                    'source': text_file.stem
                }
        
        logger.info(f"Extracted {len(paragraphs)} paragraphs from {text_file.name}")
    
    def process_jsonl_file(self, jsonl_file: Path) -> Iterator[Dict]:
        """Process JSONL metadata file."""
        logger.info(f"Processing JSONL file: {jsonl_file.name}")
        
        count = 0
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if 'text' in data and len(data['text']) > 50:
                        yield {
                            'id': count,
                            'title': data.get('title', f"Document {count}"),
                            'content': data['text'],
                            'source': jsonl_file.stem,
                            'url': data.get('url', ''),
                            'timestamp': data.get('timestamp', '')
                        }
                        count += 1
                except Exception as e:
                    continue
        
        logger.info(f"Extracted {count} records from {jsonl_file.name}")
    
    def clean_pashto_text(self, text: str) -> str:
        """Clean and normalize Pashto text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-Pashto characters (keep basic punctuation)
        text = re.sub(r'[^\u0621-\u06FF\u0750-\u077F\s\.\,\?\!\:\;\(\)\[\]\{\}\"\'0-9]', '', text)
        
        # Remove very short lines
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
        
        return '\n'.join(lines).strip()
    
    def create_training_corpus(self, output_file: str = "pashto_training_corpus.txt") -> str:
        """Create a large training corpus from all archives."""
        logger.info("🚀 Creating comprehensive Pashto training corpus...")
        
        corpus_path = self.output_path / output_file
        total_documents = 0
        total_words = 0
        
        with open(corpus_path, 'w', encoding='utf-8') as corpus_file:
            # Process all available data sources
            
            # 1. Process extracted directories
            for directory in ["pus_news_2020_100K", "pus_wikipedia_2021_30K"]:
                dir_path = self.archive_path / directory
                if dir_path.exists():
                    for sql_file in dir_path.glob("*.sql"):
                        for record in self.process_sql_import(sql_file):
                            clean_content = self.clean_pashto_text(record['content'])
                            if clean_content:
                                corpus_file.write(clean_content + '\n\n')
                                total_documents += 1
                                total_words += len(clean_content.split())
            
            # 2. Process compressed text files
            for location in self.archive_locations:
                if location.exists():
                    for gz_file in location.glob("ps*.txt.gz"):
                        try:
                            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                                content = f.read()
                                clean_content = self.clean_pashto_text(content)
                                if clean_content:
                                    corpus_file.write(clean_content + '\n\n')
                                    paragraphs = len(clean_content.split('\n\n'))
                                    total_documents += paragraphs
                                    total_words += len(clean_content.split())
                        except Exception as e:
                            logger.warning(f"Could not process {gz_file}: {e}")
            
            # 3. Process JSONL metadata files
            for location in self.archive_locations:
                if location.exists():
                    for jsonl_file in location.glob("*.jsonl*"):
                        if not jsonl_file.name.endswith('.gz'):
                            continue
                        
                        try:
                            with gzip.open(jsonl_file, 'rt', encoding='utf-8') as f:
                                for line in f:
                                    try:
                                        data = json.loads(line.strip())
                                        if 'text' in data:
                                            clean_content = self.clean_pashto_text(data['text'])
                                            if clean_content and len(clean_content.split()) > 10:
                                                corpus_file.write(clean_content + '\n\n')
                                                total_documents += 1
                                                total_words += len(clean_content.split())
                                    except:
                                        continue
                        except Exception as e:
                            logger.warning(f"Could not process {jsonl_file}: {e}")
            
            # 4. Process existing text corpus files
            text_corpus_path = self.archive_path / "pashto-text-dataset"
            if text_corpus_path.exists():
                for txt_file in text_corpus_path.glob("*.txt"):
                    try:
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            clean_content = self.clean_pashto_text(content)
                            if clean_content:
                                corpus_file.write(clean_content + '\n\n')
                                paragraphs = len(clean_content.split('\n\n'))
                                total_documents += paragraphs
                                total_words += len(clean_content.split())
                    except Exception as e:
                        logger.warning(f"Could not process {txt_file}: {e}")
        
        # Create corpus statistics
        stats = {
            "total_documents": total_documents,
            "total_words": total_words,
            "corpus_size_mb": corpus_path.stat().st_size / (1024 * 1024),
            "average_words_per_document": total_words / max(total_documents, 1)
        }
        
        stats_path = self.output_path / "corpus_statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Corpus created successfully!")
        logger.info(f"📊 Statistics:")
        logger.info(f"   📄 Documents: {total_documents:,}")
        logger.info(f"   📝 Words: {total_words:,}")
        logger.info(f"   💾 Size: {stats['corpus_size_mb']:.1f} MB")
        logger.info(f"   📋 Avg words/doc: {stats['average_words_per_document']:.1f}")
        logger.info(f"   📁 Saved to: {corpus_path}")
        
        return str(corpus_path)
    
    def create_vocabulary(self, corpus_path: str) -> str:
        """Create vocabulary file from corpus."""
        logger.info("📝 Creating vocabulary from corpus...")
        
        vocab_path = self.output_path / "pashto_vocabulary.txt"
        word_counts = {}
        
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                words = re.findall(r'[\u0621-\u06FF\u0750-\u077F]+', line.lower())
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_vocab = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        with open(vocab_path, 'w', encoding='utf-8') as f:
            for word, count in sorted_vocab:
                f.write(f"{word}\t{count}\n")
        
        logger.info(f"✅ Vocabulary created: {len(sorted_vocab):,} unique words")
        logger.info(f"📁 Saved to: {vocab_path}")
        
        return str(vocab_path)
    
    def sample_corpus(self, corpus_path: str, sample_size: int = 1000) -> str:
        """Create a sample of the corpus for quick testing."""
        logger.info(f"📋 Creating sample corpus ({sample_size} documents)...")
        
        sample_path = self.output_path / f"pashto_sample_{sample_size}.txt"
        
        with open(corpus_path, 'r', encoding='utf-8') as f:
            documents = f.read().split('\n\n')
        
        # Take every nth document to get a representative sample
        step = max(1, len(documents) // sample_size)
        sample_docs = documents[::step][:sample_size]
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(sample_docs))
        
        logger.info(f"✅ Sample created: {len(sample_docs)} documents")
        logger.info(f"📁 Saved to: {sample_path}")
        
        return str(sample_path)

def main():
    """Main execution function."""
    print("🗂️ ZamAI Big Data Archive Processor")
    print("=" * 50)
    
    processor = PashtoArchiveProcessor()
    
    # Create comprehensive training corpus
    corpus_path = processor.create_training_corpus()
    
    # Create vocabulary
    vocab_path = processor.create_vocabulary(corpus_path)
    
    # Create samples for testing
    sample_1k = processor.sample_corpus(corpus_path, 1000)
    sample_10k = processor.sample_corpus(corpus_path, 10000)
    
    print(f"\n🎯 Processing Complete!")
    print(f"📁 All files saved to: {processor.output_path}")
    print(f"\n📊 Generated Files:")
    print(f"   🗂️ Full Corpus: {corpus_path}")
    print(f"   📝 Vocabulary: {vocab_path}")
    print(f"   📋 Sample 1K: {sample_1k}")
    print(f"   📋 Sample 10K: {sample_10k}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review corpus quality: head -100 {corpus_path}")
    print(f"   2. Train base model: python train_base_model.py --corpus {corpus_path}")
    print(f"   3. Fine-tune with your high-quality dataset")

if __name__ == "__main__":
    main()
