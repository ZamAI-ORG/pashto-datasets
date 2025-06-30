#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ZamAI Data Augmentation Strategy
Expand the current 137 examples to 1000+ examples for better fine-tuning results.
"""

import json
import random
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import re

class PashtoDataAugmentation:
    def __init__(self, original_dataset_path: str):
        """Initialize with the original dataset."""
        self.original_dataset_path = original_dataset_path
        self.original_data = self.load_original_data()
        
    def load_original_data(self) -> List[Dict]:
        """Load the original JSONL dataset."""
        data = []
        with open(self.original_dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data
    
    def create_variations(self, example: Dict) -> List[Dict]:
        """Create variations of a single example."""
        variations = []
        instruction = example['instruction']
        response = example['response']
        category = example.get('category', 'general')
        
        # Method 1: Question reformulation
        variations.extend(self.reformulate_questions(instruction, response, category))
        
        # Method 2: Response style variations
        variations.extend(self.create_response_variations(instruction, response, category))
        
        # Method 3: Context expansion
        variations.extend(self.expand_context(instruction, response, category))
        
        return variations
    
    def reformulate_questions(self, instruction: str, response: str, category: str) -> List[Dict]:
        """Create different ways to ask the same question."""
        variations = []
        
        # Pashto question reformulation patterns
        reformulation_patterns = {
            'tutor_chat': [
                lambda q: q.replace('راته وویایه', 'زه غواړم پوښتنه وکړم'),
                lambda q: q.replace('څنګه', 'په کومه ډول'),
                lambda q: q.replace('ولې', 'د کوم دلیل له امله'),
                lambda q: q.replace('کله', 'په کوم وخت کې'),
            ],
            'news_summarization': [
                lambda q: q.replace('لنډیز', 'خلاصه'),
                lambda q: q.replace('راته ورکړه', 'چمتو کړه'),
                lambda q: q.replace('دا متن', 'دغه لیکنه'),
            ],
            'business_automation': [
                lambda q: q.replace('لیک', 'خط'),
                lambda q: q.replace('ولیکه', 'جوړ کړه'),
                lambda q: q.replace('سوداګرۍ', 'تجارت'),
            ]
        }
        
        patterns = reformulation_patterns.get(category, [])
        for pattern in patterns:
            try:
                new_instruction = pattern(instruction)
                if new_instruction != instruction:
                    variations.append({
                        'instruction': new_instruction,
                        'response': response,
                        'category': category,
                        'augmentation_method': 'question_reformulation'
                    })
            except:
                continue
                
        return variations
    
    def create_response_variations(self, instruction: str, response: str, category: str) -> List[Dict]:
        """Create different response styles for the same instruction."""
        variations = []
        
        # Response style templates
        if category == 'tutor_chat':
            # More detailed explanation
            detailed_response = f"دا یوه ښه پوښتنه ده. {response} که تاسو نور معلومات غواړئ، زه دلته یم."
            variations.append({
                'instruction': instruction,
                'response': detailed_response,
                'category': category,
                'augmentation_method': 'detailed_response'
            })
            
            # Simplified response
            if len(response) > 100:
                simplified = response[:response.find('.')+1] if '.' in response else response[:50] + '...'
                variations.append({
                    'instruction': instruction,
                    'response': simplified,
                    'category': category,
                    'augmentation_method': 'simplified_response'
                })
        
        elif category == 'business_automation':
            # Formal version
            formal_response = f"درناوي پاملرنه، {response} له درناوي سره."
            variations.append({
                'instruction': instruction,
                'response': formal_response,
                'category': category,
                'augmentation_method': 'formal_response'
            })
        
        return variations
    
    def expand_context(self, instruction: str, response: str, category: str) -> List[Dict]:
        """Expand context by adding related information."""
        variations = []
        
        context_expansions = {
            'cultural_content': [
                "د افغانستان د کلتور په اړه",
                "د پښتونولۍ دودونو په اړه",
                "د دودیزو دستګاوونو په اړه"
            ],
            'islamic_content': [
                "د اسلامي تعلیماتو له مخې",
                "د قرآن او حدیثونو په رڼا کې",
                "د اسلامي فقهې له نظره"
            ],
            'language_learning': [
                "د پښتو ژبې د زده کړې لپاره",
                "د ګرامر د ښه پوهیدو لپاره",
                "د ژبې د ښکلا لپاره"
            ]
        }
        
        expansions = context_expansions.get(category, [])
        for expansion in expansions:
            new_instruction = f"{expansion} {instruction}"
            new_response = f"{expansion}: {response}"
            variations.append({
                'instruction': new_instruction,
                'response': new_response,
                'category': category,
                'augmentation_method': 'context_expansion'
            })
        
        return variations
    
    def generate_synthetic_examples(self, category: str, count: int) -> List[Dict]:
        """Generate completely new synthetic examples based on patterns."""
        synthetic_examples = []
        
        # Templates for different categories
        templates = {
            'tutor_chat': [
                {
                    'instruction_template': 'د {} په اړه راته معلومات ورکړه',
                    'response_template': '{} یو مهم موضوع دی. دا په {} کې کارول کیږي.',
                    'topics': ['ساینس', 'ریاضي', 'تاریخ', 'جغرافیه', 'ادبیات']
                }
            ],
            'business_automation': [
                {
                    'instruction_template': 'د {} لپاره یو مسلکي لیک ولیکه',
                    'response_template': 'درناوي ملګري، زه ستاسو ته د {} په اړه لیکم.',
                    'topics': ['وظیفه غوښتنه', 'د پیسو غوښتنه', 'د ناروغۍ اطلاع', 'د دفتر کار']
                }
            ],
            'cultural_content': [
                {
                    'instruction_template': 'د {} دود څنګه دی؟',
                    'response_template': 'د {} دود زموږ د کلتور یوه مهمه برخه ده.',
                    'topics': ['واده', 'اختر', 'کلونۍ', 'جنازه', 'مېلمستیا']
                }
            ]
        }
        
        category_templates = templates.get(category, [])
        for template in category_templates:
            for topic in template['topics'][:count]:
                synthetic_examples.append({
                    'instruction': template['instruction_template'].format(topic),
                    'response': template['response_template'].format(topic, topic),
                    'category': category,
                    'augmentation_method': 'synthetic_generation'
                })
        
        return synthetic_examples
    
    def augment_dataset(self, target_size: int = 1000) -> List[Dict]:
        """Main method to augment the dataset to target size."""
        print(f"📊 Original dataset size: {len(self.original_data)} examples")
        
        augmented_data = []
        
        # Add original data
        augmented_data.extend(self.original_data)
        
        # Calculate how many more examples we need
        remaining_needed = target_size - len(self.original_data)
        
        print(f"🎯 Target size: {target_size}")
        print(f"📈 Need to generate: {remaining_needed} more examples")
        
        # Create variations of existing examples
        variations_created = 0
        for example in self.original_data:
            if variations_created >= remaining_needed // 2:
                break
            variations = self.create_variations(example)
            augmented_data.extend(variations)
            variations_created += len(variations)
        
        print(f"✅ Created {variations_created} variations")
        
        # Generate synthetic examples for underrepresented categories
        categories_needing_boost = ['business_automation', 'cultural_content', 'islamic_content', 'language_learning']
        
        synthetic_created = 0
        remaining_synthetic = remaining_needed - variations_created
        
        for category in categories_needing_boost:
            if synthetic_created >= remaining_synthetic:
                break
            count_per_category = min(50, remaining_synthetic // len(categories_needing_boost))
            synthetic = self.generate_synthetic_examples(category, count_per_category)
            augmented_data.extend(synthetic)
            synthetic_created += len(synthetic)
        
        print(f"🤖 Generated {synthetic_created} synthetic examples")
        print(f"📊 Final dataset size: {len(augmented_data)} examples")
        
        return augmented_data
    
    def save_augmented_dataset(self, augmented_data: List[Dict], output_dir: str = "zamai_augmented_dataset"):
        """Save the augmented dataset in multiple formats."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save as JSONL
        jsonl_path = output_path / "zamai_augmented_dataset.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for example in augmented_data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        # Save as JSON
        json_path = output_path / "zamai_augmented_dataset.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(augmented_data, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        csv_path = output_path / "zamai_augmented_dataset.csv"
        df = pd.DataFrame(augmented_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Create dataset info
        info = {
            "total_examples": len(augmented_data),
            "categories": {},
            "augmentation_methods": {}
        }
        
        for example in augmented_data:
            category = example.get('category', 'unknown')
            method = example.get('augmentation_method', 'original')
            
            info["categories"][category] = info["categories"].get(category, 0) + 1
            info["augmentation_methods"][method] = info["augmentation_methods"].get(method, 0) + 1
        
        info_path = output_path / "dataset_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 Augmented dataset saved to: {output_path}")
        print(f"   📄 JSONL: {jsonl_path}")
        print(f"   📄 JSON: {json_path}")
        print(f"   📄 CSV: {csv_path}")
        print(f"   📊 Info: {info_path}")
        
        return output_path

def main():
    """Main execution function."""
    print("🚀 ZamAI Data Augmentation Pipeline")
    print("=" * 50)
    
    # Initialize augmentation
    original_dataset = "zamai_final_dataset/zamai_training_dataset.jsonl"
    
    if not Path(original_dataset).exists():
        print(f"❌ Original dataset not found: {original_dataset}")
        print("Please run zamai_training_dataset.py first to create the base dataset.")
        return
    
    augmenter = PashtoDataAugmentation(original_dataset)
    
    # Generate augmented dataset
    target_sizes = [500, 1000, 2000]
    
    print(f"\n📊 Current dataset analysis:")
    category_counts = {}
    for example in augmenter.original_data:
        cat = example.get('category', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for category, count in category_counts.items():
        print(f"   {category}: {count} examples")
    
    print(f"\n🎯 Augmentation options:")
    for i, size in enumerate(target_sizes, 1):
        print(f"   {i}. Generate {size} total examples")
    
    choice = input(f"\nSelect augmentation target (1-{len(target_sizes)}, or Enter for 1000): ").strip()
    
    if choice == "":
        target_size = 1000
    else:
        try:
            target_size = target_sizes[int(choice) - 1]
        except (ValueError, IndexError):
            target_size = 1000
    
    print(f"\n🔄 Generating {target_size} examples...")
    augmented_data = augmenter.augment_dataset(target_size)
    
    # Save augmented dataset
    output_path = augmenter.save_augmented_dataset(augmented_data)
    
    print(f"\n✅ Data augmentation complete!")
    print(f"📈 Dataset expanded from 137 to {len(augmented_data)} examples")
    print(f"\n🚀 Next steps:")
    print(f"   1. Review the augmented dataset quality")
    print(f"   2. Train your model with: python zamai_model_trainer.py --dataset_path {output_path}/zamai_augmented_dataset.jsonl")
    print(f"   3. Test the improved model performance")

if __name__ == "__main__":
    main()
