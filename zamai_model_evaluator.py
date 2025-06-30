#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ZamAI Model Evaluation Suite
Comprehensive evaluation of fine-tuned Pashto models across different tasks.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import re
import time

class PashtoModelEvaluator:
    def __init__(self, model_path: str, test_dataset_path: str):
        """Initialize evaluator with model and test dataset."""
        self.model_path = model_path
        self.test_dataset_path = test_dataset_path
        self.load_model()
        self.load_test_data()
        
    def load_model(self):
        """Load the fine-tuned model and tokenizer."""
        print(f"📥 Loading model from: {self.model_path}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def load_test_data(self):
        """Load test dataset."""
        print(f"📥 Loading test data from: {self.test_dataset_path}")
        try:
            self.test_data = []
            with open(self.test_dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.test_data.append(json.loads(line.strip()))
            print(f"✅ Loaded {len(self.test_data)} test examples")
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            raise
    
    def generate_response(self, instruction: str, max_length: int = 512) -> str:
        """Generate response for a given instruction."""
        # Format prompt
        prompt = f"""د لاندې پوښتنې ته پښتو کې ځواب ورکړه:

پوښتنه: {instruction}

ځواب:"""
        
        # Tokenize
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = inputs.cuda()
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part
        if "ځواب:" in full_response:
            response = full_response.split("ځواب:")[-1].strip()
        else:
            response = full_response[len(prompt):].strip()
        
        return response
    
    def evaluate_pashto_quality(self, text: str) -> float:
        """Evaluate if the text is proper Pashto (basic heuristics)."""
        if not text:
            return 0.0
        
        # Check for Pashto Unicode range
        pashto_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                # Pashto Unicode ranges
                if '\u0621' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F':
                    pashto_chars += 1
        
        if total_chars == 0:
            return 0.0
        
        pashto_ratio = pashto_chars / total_chars
        
        # Additional checks
        has_proper_structure = any(word in text for word in ['د', 'په', 'او', 'یا', 'که', 'چې'])
        
        # Final score
        quality_score = pashto_ratio * 0.8
        if has_proper_structure:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def evaluate_relevance(self, instruction: str, response: str) -> float:
        """Evaluate response relevance to instruction (basic keyword matching)."""
        if not response:
            return 0.0
        
        # Extract key terms from instruction
        instruction_words = re.findall(r'[\u0621-\u06FF\u0750-\u077F]+', instruction.lower())
        response_words = re.findall(r'[\u0621-\u06FF\u0750-\u077F]+', response.lower())
        
        if not instruction_words:
            return 0.5  # Neutral if no key words
        
        # Calculate overlap
        overlap = len(set(instruction_words) & set(response_words))
        relevance_score = overlap / len(instruction_words)
        
        return min(relevance_score, 1.0)
    
    def evaluate_completeness(self, response: str) -> float:
        """Evaluate response completeness (length and structure)."""
        if not response:
            return 0.0
        
        # Word count (approximate for Pashto)
        words = len(re.findall(r'[\u0621-\u06FF\u0750-\u077F]+', response))
        
        # Length scoring
        if words >= 20:
            length_score = 1.0
        elif words >= 10:
            length_score = 0.8
        elif words >= 5:
            length_score = 0.6
        elif words >= 2:
            length_score = 0.4
        else:
            length_score = 0.2
        
        # Structure scoring (punctuation, coherence indicators)
        has_punctuation = any(p in response for p in ['.', '?', '!', '،', '؟', '۔'])
        structure_score = 0.2 if has_punctuation else 0.0
        
        return min(length_score + structure_score, 1.0)
    
    def evaluate_category_performance(self, category: str) -> Dict[str, Any]:
        """Evaluate model performance on specific category."""
        category_examples = [ex for ex in self.test_data if ex.get('category') == category]
        
        if not category_examples:
            return {"error": f"No examples found for category: {category}"}
        
        results = {
            "category": category,
            "total_examples": len(category_examples),
            "pashto_quality_scores": [],
            "relevance_scores": [],
            "completeness_scores": [],
            "response_times": [],
            "examples": []
        }
        
        print(f"\n🔍 Evaluating category: {category} ({len(category_examples)} examples)")
        
        for i, example in enumerate(category_examples):
            print(f"   Processing {i+1}/{len(category_examples)}...", end='\r')
            
            instruction = example['instruction']
            expected_response = example['response']
            
            # Generate response
            start_time = time.time()
            generated_response = self.generate_response(instruction)
            response_time = time.time() - start_time
            
            # Evaluate
            pashto_quality = self.evaluate_pashto_quality(generated_response)
            relevance = self.evaluate_relevance(instruction, generated_response)
            completeness = self.evaluate_completeness(generated_response)
            
            results["pashto_quality_scores"].append(pashto_quality)
            results["relevance_scores"].append(relevance)
            results["completeness_scores"].append(completeness)
            results["response_times"].append(response_time)
            
            # Store example for review
            if i < 3:  # Store first 3 examples for manual review
                results["examples"].append({
                    "instruction": instruction,
                    "expected": expected_response,
                    "generated": generated_response,
                    "pashto_quality": pashto_quality,
                    "relevance": relevance,
                    "completeness": completeness
                })
        
        # Calculate averages
        results["avg_pashto_quality"] = np.mean(results["pashto_quality_scores"])
        results["avg_relevance"] = np.mean(results["relevance_scores"])
        results["avg_completeness"] = np.mean(results["completeness_scores"])
        results["avg_response_time"] = np.mean(results["response_times"])
        
        # Overall score
        results["overall_score"] = (
            results["avg_pashto_quality"] * 0.4 +
            results["avg_relevance"] * 0.4 +
            results["avg_completeness"] * 0.2
        )
        
        print(f"\n✅ Category {category} completed")
        
        return results
    
    def full_evaluation(self) -> Dict[str, Any]:
        """Run full evaluation across all categories."""
        print("🚀 Starting Full Model Evaluation")
        print("=" * 50)
        
        # Get all categories
        categories = list(set(ex.get('category', 'unknown') for ex in self.test_data))
        
        evaluation_results = {
            "model_path": self.model_path,
            "test_dataset_path": self.test_dataset_path,
            "total_test_examples": len(self.test_data),
            "categories": categories,
            "category_results": {},
            "overall_metrics": {}
        }
        
        # Evaluate each category
        all_scores = {"pashto_quality": [], "relevance": [], "completeness": [], "overall": []}
        
        for category in categories:
            category_result = self.evaluate_category_performance(category)
            evaluation_results["category_results"][category] = category_result
            
            if "error" not in category_result:
                all_scores["pashto_quality"].extend(category_result["pashto_quality_scores"])
                all_scores["relevance"].extend(category_result["relevance_scores"])
                all_scores["completeness"].extend(category_result["completeness_scores"])
                all_scores["overall"].append(category_result["overall_score"])
        
        # Calculate overall metrics
        evaluation_results["overall_metrics"] = {
            "avg_pashto_quality": np.mean(all_scores["pashto_quality"]),
            "avg_relevance": np.mean(all_scores["relevance"]),
            "avg_completeness": np.mean(all_scores["completeness"]),
            "overall_score": np.mean(all_scores["overall"]),
            "total_evaluated_examples": len(all_scores["pashto_quality"])
        }
        
        return evaluation_results
    
    def create_evaluation_report(self, results: Dict[str, Any], output_path: str = "evaluation_report.json"):
        """Create detailed evaluation report."""
        
        # Save full results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Create summary report
        summary_path = output_path.replace('.json', '_summary.txt')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("ZamAI Pashto Model Evaluation Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Model: {results['model_path']}\n")
            f.write(f"Test Dataset: {results['test_dataset_path']}\n")
            f.write(f"Total Test Examples: {results['total_test_examples']}\n\n")
            
            f.write("OVERALL PERFORMANCE:\n")
            f.write("-" * 20 + "\n")
            overall = results['overall_metrics']
            f.write(f"Overall Score: {overall['overall_score']:.3f}/1.000\n")
            f.write(f"Pashto Quality: {overall['avg_pashto_quality']:.3f}/1.000\n")
            f.write(f"Relevance: {overall['avg_relevance']:.3f}/1.000\n")
            f.write(f"Completeness: {overall['avg_completeness']:.3f}/1.000\n\n")
            
            f.write("CATEGORY BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            
            for category, result in results['category_results'].items():
                if "error" not in result:
                    f.write(f"\n{category.upper()}:\n")
                    f.write(f"  Examples: {result['total_examples']}\n")
                    f.write(f"  Overall Score: {result['overall_score']:.3f}\n")
                    f.write(f"  Pashto Quality: {result['avg_pashto_quality']:.3f}\n")
                    f.write(f"  Relevance: {result['avg_relevance']:.3f}\n")
                    f.write(f"  Completeness: {result['avg_completeness']:.3f}\n")
                    f.write(f"  Avg Response Time: {result['avg_response_time']:.2f}s\n")
            
            # Performance interpretation
            f.write(f"\n\nPERFORMANCE INTERPRETATION:\n")
            f.write("-" * 30 + "\n")
            
            overall_score = overall['overall_score']
            if overall_score >= 0.8:
                f.write("🟢 EXCELLENT: Model performs very well across all tasks\n")
            elif overall_score >= 0.6:
                f.write("🟡 GOOD: Model shows solid performance, some improvement areas\n")
            elif overall_score >= 0.4:
                f.write("🟠 FAIR: Model has basic capabilities, needs significant improvement\n")
            else:
                f.write("🔴 POOR: Model needs major improvements or more training data\n")
        
        print(f"\n📊 Evaluation complete!")
        print(f"📄 Full results: {output_path}")
        print(f"📋 Summary report: {summary_path}")
        
        return output_path, summary_path

def create_test_split(dataset_path: str, test_ratio: float = 0.2) -> str:
    """Create a test split from the full dataset."""
    print(f"📂 Creating test split from: {dataset_path}")
    
    # Load full dataset
    data = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    
    # Shuffle and split
    np.random.shuffle(data)
    test_size = int(len(data) * test_ratio)
    test_data = data[:test_size]
    
    # Save test split
    test_path = dataset_path.replace('.jsonl', '_test.jsonl')
    with open(test_path, 'w', encoding='utf-8') as f:
        for example in test_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Test split created: {test_path} ({len(test_data)} examples)")
    return test_path

def main():
    """Main execution function."""
    print("🔍 ZamAI Model Evaluation Suite")
    print("=" * 40)
    
    # Get model path
    model_path = input("Enter path to fine-tuned model (or 'microsoft/DialoGPT-medium' for baseline): ").strip()
    if not model_path:
        model_path = "microsoft/DialoGPT-medium"
    
    # Get dataset path
    dataset_path = input("Enter path to dataset (default: zamai_final_dataset/zamai_training_dataset.jsonl): ").strip()
    if not dataset_path:
        dataset_path = "zamai_final_dataset/zamai_training_dataset.jsonl"
    
    # Check if test split exists
    test_path = dataset_path.replace('.jsonl', '_test.jsonl')
    if not Path(test_path).exists():
        print(f"📊 Test split not found. Creating from {dataset_path}...")
        test_path = create_test_split(dataset_path)
    
    try:
        # Initialize evaluator
        evaluator = PashtoModelEvaluator(model_path, test_path)
        
        # Run evaluation
        results = evaluator.full_evaluation()
        
        # Create report
        report_path, summary_path = evaluator.create_evaluation_report(results)
        
        # Print quick summary
        print(f"\n🎯 QUICK SUMMARY:")
        overall = results['overall_metrics']
        print(f"Overall Score: {overall['overall_score']:.3f}/1.000")
        print(f"Pashto Quality: {overall['avg_pashto_quality']:.3f}")
        print(f"Relevance: {overall['avg_relevance']:.3f}")
        print(f"Completeness: {overall['avg_completeness']:.3f}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        print("Make sure your model and dataset paths are correct.")

if __name__ == "__main__":
    main()
