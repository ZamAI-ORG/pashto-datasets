#!/usr/bin/env python3
"""
ZamAI Pashto Training Dataset Creator

This script creates a comprehensive, high-quality training dataset for Pashto language models
based on the ZamAI text strategy. It formats data for tutor bots, chat assistants, and 
business automation tasks.

Author: ZamAI Dataset Team
Date: June 30, 2025
"""

import json
import csv
import os
import re
import random
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

class PashtoDatasetCreator:
    def __init__(self, output_dir: str = "zamai_final_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Data paths
        self.data_root = Path("/workspaces/Pashto-Dataset-Creating-Dataset/Pashto-Data")
        
        # Dataset categories
        self.datasets = {
            "tutor_chat": [],
            "general_qa": [],
            "news_summarization": [],
            "business_automation": [],
            "cultural_content": [],
            "islamic_content": [],
            "language_learning": []
        }
        
    def load_gathered_data(self) -> List[Dict]:
        """Load the gathered news and article data"""
        data = []
        gathered_path = self.data_root / "gathered_data"
        
        for file_path in gathered_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        data.extend(file_data)
                    else:
                        data.append(file_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return data
    
    def load_text_corpus(self) -> str:
        """Load the main Pashto text corpus"""
        corpus_path = self.data_root / "pashto-text-dataset" / "pashto_text_data.txt"
        try:
            with open(corpus_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading corpus: {e}")
            return ""
    
    def load_metadata(self) -> List[Dict]:
        """Load metadata from JSONL files"""
        metadata = []
        metadata_path = self.data_root / "Pashto_High_value_dataset" / "pashto_meta_data.jsonl"
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        metadata.append(json.loads(line))
        except Exception as e:
            print(f"Error loading metadata: {e}")
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize Pashto text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Pashto punctuation
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\s\d\.\!\?\,\:\;\-\(\)\"\']+', '', text)
        
        return text.strip()
    
    def create_tutor_chat_data(self, corpus: str, articles: List[Dict]) -> List[Dict]:
        """Create tutor and chat conversation data"""
        tutor_data = []
        
        # Afghanistan geography and culture questions
        afghanistan_qa = [
            {
                "instruction": "د افغانستان پایتخت چه شی دی؟",
                "response": "د افغانستان پایتخت کابل دی. کابل د افغانستان تر ټولو لوی ښار او د دغه هیواد سیاسي، اقتصادي او کلتوري مرکز دی."
            },
            {
                "instruction": "د افغانستان رسمي ژبې کومې دي؟",
                "response": "د افغانستان رسمي ژبې پښتو او دري دي. پښتو د افغان ولس اصلي ژبه ده او دري هم د پراخو برخو لخوا کارول کیږي."
            },
            {
                "instruction": "د پښتو ژبې د زده کړې لپاره ماته لارښوونه ورکړه",
                "response": "د پښتو ژبې د زده کړې لپاره دا مرحلې تعقیب کړئ: ۱) د پښتو الفبا او املا زده کړئ ۲) اساسي کلمې او جملې تمرین کړئ ۳) ورځني استعمال ته پاملرنه وکړئ ۴) د پښتو شاعرۍ او ادبیاتو لوستل پیل کړئ ۵) د ویناوالانو سره خبرې اترې وکړئ"
            },
            {
                "instruction": "د افغانستان مهم تاریخي ځایونه کوم دي؟",
                "response": "د افغانستان مهم تاریخي ځایونه پدې دي: د بامیانو تاریخي مجسمې، د ننګرهار تاریخي بودایي ځایونه، د غزني تاریخي ماڼۍ، د هرات جامع جومات، د کندهار زرغونه خرقه، او د کابل د بالاحصار کلا."
            },
            {
                "instruction": "د پښتنو دودونه او رواجونه راته ووایه",
                "response": "د پښتنو مهم دودونه دا دي: میلمستیا (د میلمه درناوی)، ننګ (د غیرتونو ساتل)، بدل (انتقام اخیستل)، پښتونولي (د پښتون ارزښتونه)، جرګه (ټولنیز پریکړه کول)، او د کورنۍ درناوی."
            }
        ]
        
        # Educational content
        education_qa = [
            {
                "instruction": "د ریاضیاتو بنسټیز مفاهیم راته وروښیه",
                "response": "د ریاضیاتو بنسټیز مفاهیم پدې دي: شمېرنه (۱، ۲، ۳...)، جمع کول (+)، لرې کول (-)، ضرب (×)، وېش (÷)، کسرونه (۱/۲، ۲/۳)، فیصدې (%)، او اندازه اخیستل (اوږدوالی، وزن، مساحت)."
            },
            {
                "instruction": "د علومو څانګې کومې دي؟",
                "response": "د علومو اصلي څانګې دا دي: فزیک (د طبیعت علم)، کیمیا (د مادو علم)، بیولوژي (د ژویو علم)، ریاضي (د شمېرونو علم)، ځمکپوهنه (د ځمکې علم)، ستورپوهنه (د اسمانو علم)، او طب (د روغتیا علم)."
            },
            {
                "instruction": "د انګلیسي ژبې زده کړه څنګه پیل کړم؟",
                "response": "د انګلیسي ژبې د زده کړې لپاره دا لارې تعقیب کړئ: ۱) د انګلیسي توري (A-Z) زده کړئ ۲) اساسي کلمې لکه شمېرې، رنګونه، کورنۍ غړي زده کړئ ۳) ساده جملې جوړول زده کړئ ۴) ورځني غږیدل او لوستل تمرین کړئ ۵) د انګلیسي فلمونه او سندرې واورئ"
            }
        ]
        
        # Language learning assistance
        language_qa = [
            {
                "instruction": "د پښتو ژبې ګرامر راته وښیه",
                "response": "د پښتو ژبې ګرامر پدې ډول دی: ۱) د ناستو ویش: نارینه او ښځینه ۲) د شمیر ویش: یوګړی او څو ګړی ۳) د حالت ویش: فاعلي، مفعولي، اضافي حالت ۴) د وخت ویش: تیر، اوسنی، راتلونکی ۵) د فعل بڼې: اوسنۍ، تیرې، امر"
            },
            {
                "instruction": "د پښتو ادبیاتو مشهور شاعران کوم دي؟",
                "response": "د پښتو ادبیاتو مشهور شاعران دا دي: خوشحال خان ختک (د پښتو شاعرۍ پلار)، رحمان بابا (د عشق شاعر)، احمد شاه ابدالي، عبدالحمید مومند، غني خان، او قلندر مومند. دا ټول د پښتو ژبې او کلتور لپاره زیات اغېز لري."
            }
        ]
        
        # Add all predefined Q&A pairs
        tutor_data.extend(afghanistan_qa)
        tutor_data.extend(education_qa)
        tutor_data.extend(language_qa)
        
        # Generate more data from articles
        for article in articles[:50]:  # Use first 50 articles
            if article.get('title') and article.get('content'):
                # Create question-answer pairs from articles
                title = self.clean_text(article['title'])
                content = self.clean_text(article['content'][:300])  # First 300 chars
                
                if len(title) > 10 and len(content) > 50:
                    qa_pair = {
                        "instruction": f"د دې ټکي په اړه ماته معلومات ورکړه: {title}",
                        "response": content
                    }
                    tutor_data.append(qa_pair)
        
        return tutor_data
    
    def create_summarization_data(self, articles: List[Dict]) -> List[Dict]:
        """Create summarization training data"""
        summarization_data = []
        
        for article in articles:
            if not article.get('content') or len(article['content']) < 200:
                continue
                
            content = self.clean_text(article['content'])
            title = self.clean_text(article.get('title', ''))
            
            if len(content) > 200:
                # Create summarization pairs
                summary_pair = {
                    "instruction": "دا متن لنډ کړه:",
                    "input": content,
                    "response": title if title else content[:100] + "..."
                }
                summarization_data.append(summary_pair)
                
                # Create explanation pairs
                if title:
                    explain_pair = {
                        "instruction": f"د دې ټکي تفصیل راکړه: {title}",
                        "response": content[:500]  # First 500 chars as explanation
                    }
                    summarization_data.append(explain_pair)
        
        return summarization_data
    
    def create_business_automation_data(self) -> List[Dict]:
        """Create business and form filling automation data"""
        business_data = [
            {
                "instruction": "د سوداګرۍ خط راته ولیکه",
                "response": "درناوي ملګري، موږ ستاسو ته زموږ د نوي محصول په اړه خبر ورکوو. موږ ډېر خوښ یو چې دا ستاسو ته وړاندې کړو. که تاسو د نورو معلوماتو اړتیا لرئ، مهرباني وکړئ زموږ سره اړیکه ونیسئ. ډېر مننه."
            },
            {
                "instruction": "د رښتون غوښتنلیک ولیکه",
                "response": "د محترم ریس ته، زه د دندې د رخصتۍ لپاره دا غوښتنلیک وړاندې کوم. زه د [نیټه] څخه تر [نیټه] پورې رخصتي ته اړتیا لرم د [دلیل] له امله. هیله لرم چې زما غوښتنه به منل شي. ډېر مننه، [نوم]"
            },
            {
                "instruction": "د پیرودلو فاکتور جوړ کړه",
                "response": "فاکتور نمبر: [شمېره]\nنیټه: [نیټه]\nپیرودونکي: [نوم]\nپته: [پته]\n\nد توکو تفصیل:\n- [د توکو نوم] × [مقدار] = [قیمت]\n- [د توکو نوم] × [مقدار] = [قیمت]\n\nټول قیمت: [مجموعه]\nمالیه: [مالیه]\nوروستي قیمت: [وروستي قیمت]"
            },
            {
                "instruction": "د غونډې راپور ولیکه",
                "response": "د غونډې راپور\nنیټه: [نیټه]\nځای: [ځای]\nګډونوال: [نومونه]\n\nد بحث ټکي:\n۱. [ټکی یو]\n۲. [ټکی دوه]\n۳. [ټکی درې]\n\nپریکړې:\n- [پریکړه یو]\n- [پریکړه دوه]\n\nراتلونکي کارونه:\n- [کار یو] (مسؤل: [نوم])\n- [کار دوه] (مسؤل: [نوم])"
            }
        ]
        
        return business_data
    
    def create_islamic_content_data(self, corpus: str) -> List[Dict]:
        """Create Islamic content and religious Q&A data"""
        islamic_data = [
            {
                "instruction": "د اسلام د پنځو ستنو په اړه راته ووایه",
                "response": "د اسلام پنځه ستنې دا دي: ۱) کلمه (د الله توحید او د محمد رسالت تصدیق) ۲) لمونځ (د ورځې پنځه وخته لمونځونه) ۳) زکات (د شتمنۍ څخه د فقیرانو حق ورکول) ۴) روژه (د رمضان میاشت روژه نیول) ۵) حج (د مکې ته زیارت که چیرې وړتیا ولري)"
            },
            {
                "instruction": "د قرآن کریم د ځانګړتیاوو په اړه راته ووایه",
                "response": "قرآن کریم د الله تعالی آخری کتاب دی چې د محمد صلی الله علیه وسلم باندې نازل شوی. دا د ۱۱۴ سورتونو او شاوخوا ۶۲۳۶ ایاتونو څخه جوړ دی. قرآن د ۲۳ کلونو په اوږدو کې نازل شوی او د ټولو مسلمانانو لپاره د ژوند د لارښوونې سرچینه ده."
            },
            {
                "instruction": "د پنجګانه لمونځ وختونه کوم دي؟",
                "response": "د پنجګانه لمونځ وختونه دا دي: ۱) د سهار لمونځ (د سپیدې څخه تر لمر پورته کیدو) ۲) د غرمې لمونځ (د لمر د ماشومۍ څخه تر ماسپښین) ۳) د ماسپښین لمونځ (د ماسپښین څخه تر لمر لویدو) ۴) د ماښام لمونځ (د لمر له لویدو وروسته) ۵) د شپې لمونځ (د ماښام څخه تر سپیدې)"
            }
        ]
        
        # Extract Islamic content from corpus
        islamic_lines = [line.strip() for line in corpus.split('\n') 
                        if any(word in line for word in ['الله', 'قرآن', 'اسلام', 'لمونځ', 'روژه'])]
        
        for line in islamic_lines[:20]:  # Use first 20 relevant lines
            if len(line) > 50:
                islamic_data.append({
                    "instruction": "د دین په اړه دا ټکی راته تشریح کړه",
                    "response": self.clean_text(line)
                })
        
        return islamic_data
    
    def create_cultural_content_data(self) -> List[Dict]:
        """Create cultural and traditional content data"""
        cultural_data = [
            {
                "instruction": "د افغانستان دودیز خواړه کوم دي؟",
                "response": "د افغانستان دودیز خواړه پدې دي: پلاو (د وریجو سره)، کباب، مانتو، بولاني، قورمه، آش، شولې پلاو، قابلي پلاو، کچالو چپلي، او نان. دا ټول د افغان کلتور مهم برخه ده."
            },
            {
                "instruction": "د افغانستان دودیز جامو په اړه راته ووایه",
                "response": "د افغانستان دودیز جامې دا دي: د نارینه وو لپاره - شلوار قمیص، چپن، پکول، تویې، او کولا. د ښځو لپاره - فرقه، شلوار قمیص، چادر، او دودیز ګاڼۍ. دا جامې د افغان کلتور ښکلا او دود ښیي."
            },
            {
                "instruction": "د پښتو ولسي سندرې کومې دي؟",
                "response": "د پښتو ولسي سندرې پدې دي: اتڼ، ملي اتڼ، د ختیځ سندرې، د سهار سندرې، د محبت سندرې، جنګي سندرې، او د واده سندرې. دا سندرې د افغان ولس د خوښۍ او غم احساسات بیانوي."
            },
            {
                "instruction": "د افغانستان مهم ورځې کومې دي؟",
                "response": "د افغانستان مهم ورځې دا دي: د استقلال ورځ (۱۹ اګست)، د جمهوریت ورځ، د کرګرانو ورځ (۱ می)، د ښوونکو ورځ، د میندو ورځ، د ماشومانو ورځ، د شاعرانو ورځ، او د مجاهدینو ورځ."
            }
        ]
        
        return cultural_data
    
    def create_general_qa_data(self, corpus: str) -> List[Dict]:
        """Create general knowledge Q&A data"""
        general_data = [
            {
                "instruction": "د نړۍ لویې سیندونه کوم دي؟",
                "response": "د نړۍ لویې سیندونه دا دي: نیل (افریقا)، امازون (سویلي امریکا)، یانګ تزی (چین)، میسیسیپي (امریکا)، یینسي (روسیه)، سندھ (د پاکستان او هند)، او د افغانستان سیندونه: آمو، کابل، هلمند، کونړ."
            },
            {
                "instruction": "د روغتیا د ساتلو لپاره څه وکړم؟",
                "response": "د روغتیا د ساتلو لپاره دا کارونه وکړئ: ۱) پاک او صحي خواړه وخورئ ۲) ورځني ورزش وکړئ ۳) کافي اوبه وښه ۴) د کافي خوب واخلئ ۵) له تنبکو او نشه ایزو توکو ډډه وکړئ ۶) دکتور ته منظم ولاړ شئ"
            },
            {
                "instruction": "د چاپیریال د ساتنې لپاره څه کولی شم؟",
                "response": "د چاپیریال د ساتنې لپاره دا کارونه کولی شئ: ۱) ونې کرل ۲) د کثافاتو سمه ویش ۳) د اوبو سپما کارونه ۴) د بریښنا کم لګښت ۵) د پلاستیک کم کارونه ۶) د عامه وسایطو کارونه ۷) د ریسایکل توکو کارونه"
            }
        ]
        
        return general_data
    
    def generate_conversation_data(self) -> List[Dict]:
        """Generate conversational training data"""
        conversation_data = [
            {
                "instruction": "سلام وروره!",
                "response": "سلام ورور! ښه راغلاست. د ماشومانو میره د خیر؟ د څه مرستې اړتیا لرئ؟"
            },
            {
                "instruction": "ستاسو حال څنګه دی؟",
                "response": "زموږ حال د الله په مهربانۍ ښه دی. ستاسو حال څنګه دی؟ د کورنۍ میره د خیر؟"
            },
            {
                "instruction": "ډېر مننه ستاسو د مرستې لپاره",
                "response": "دا زموږ خوښي ده چې ستاسو سره مرسته وکړو. که بل ځل د مرستې اړتیا ولرئ، موږ دلته یو."
            },
            {
                "instruction": "دا څومره وخت نیسي؟",
                "response": "دا د کار ډول ته پورې اړه لري. عموماً دا ډېر وخت نه نیسي. که تاسو دقیق معلومات راکړئ، زه دی د ټولو ښه وخت ورکولی شم."
            },
            {
                "instruction": "زه دا نه پوهیږم",
                "response": "هیڅ اندېښنه مه کوئ! دا عادي خبره ده. راځئ چې دا ګام په ګام تشریح کړم. کومه برخه ستاسو ته ستونزمنه ښکاري؟"
            }
        ]
        
        return conversation_data
    
    def save_datasets(self):
        """Save all datasets in different formats"""
        print("Creating comprehensive Pashto training dataset...")
        
        # Load data sources
        articles = self.load_gathered_data()
        corpus = self.load_text_corpus()
        
        print(f"Loaded {len(articles)} articles")
        print(f"Loaded corpus with {len(corpus)} characters")
        
        # Create datasets
        self.datasets["tutor_chat"] = self.create_tutor_chat_data(corpus, articles)
        self.datasets["general_qa"] = self.create_general_qa_data(corpus)
        self.datasets["news_summarization"] = self.create_summarization_data(articles)
        self.datasets["business_automation"] = self.create_business_automation_data()
        self.datasets["cultural_content"] = self.create_cultural_content_data()
        self.datasets["islamic_content"] = self.create_islamic_content_data(corpus)
        self.datasets["language_learning"] = self.generate_conversation_data()
        
        # Combine all datasets
        all_data = []
        for category, data in self.datasets.items():
            for item in data:
                item["category"] = category
                all_data.append(item)
        
        # Shuffle for better training
        random.shuffle(all_data)
        
        print(f"\nDataset Summary:")
        for category, data in self.datasets.items():
            print(f"  {category}: {len(data)} examples")
        print(f"  Total: {len(all_data)} examples")
        
        # Save in JSONL format (for HuggingFace)
        with open(self.output_dir / "zamai_training_dataset.jsonl", 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Save in JSON format
        with open(self.output_dir / "zamai_training_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # Save in CSV format
        df = pd.DataFrame(all_data)
        df.to_csv(self.output_dir / "zamai_training_dataset.csv", index=False, encoding='utf-8')
        
        # Save category-specific datasets
        for category, data in self.datasets.items():
            if data:
                category_file = self.output_dir / f"{category}_dataset.jsonl"
                with open(category_file, 'w', encoding='utf-8') as f:
                    for item in data:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Create dataset info file
        dataset_info = {
            "name": "ZamAI Pashto Training Dataset",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "total_examples": len(all_data),
            "categories": {category: len(data) for category, data in self.datasets.items()},
            "description": "Comprehensive Pashto language dataset for tutor bots, chat assistants, and business automation",
            "usage": "Fine-tuning language models for Pashto NLP tasks",
            "format": "instruction-response pairs with optional input field"
        }
        
        with open(self.output_dir / "dataset_info.json", 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        print(f"\nDataset saved to: {self.output_dir}")
        print("Files created:")
        print("  - zamai_training_dataset.jsonl (for HuggingFace)")
        print("  - zamai_training_dataset.json")
        print("  - zamai_training_dataset.csv")
        print("  - dataset_info.json")
        print("  - Individual category files")

def main():
    """Main function to create the dataset"""
    creator = PashtoDatasetCreator()
    creator.save_datasets()
    print("\n✅ ZamAI Pashto training dataset created successfully!")
    print("\nNext steps:")
    print("1. Upload to HuggingFace Hub as private dataset")
    print("2. Use for fine-tuning Mistral, Llama, or Phi models")
    print("3. Deploy via HuggingFace Inference API")
    print("4. Test with Gradio interface")

if __name__ == "__main__":
    main()
