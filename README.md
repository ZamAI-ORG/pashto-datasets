# Pashto Datasets

Datasets and notebooks for Pashto language work in ZamAI Labs.

- Website: https://zamai.dev
- Labs org: https://github.com/ZamAI-ORG


# Pashto Datasets

Datasets and notebooks for Pashto language work in ZamAI Labs.

- Website: https://zamai.dev
- Labs org: https://github.com/ZamAI-ORG


# Pashto Datasets

Datasets and notebooks for Pashto language work in ZamAI Labs.

- Website: https://zamai.dev
- Labs org: https://github.com/ZamAI-ORG


# 🇦🇫 ZamAI - Comprehensive Pashto Language Dataset

**د پښتو ژبې د ذکي مرستیال لپاره جامع ډیټاسیټ**

Welcome to the **ZamAI Pashto Dataset** repository! This project implements a complete text-first strategy for building, fine-tuning, and deploying Pashto language models using HuggingFace Pro infrastructure.

## 🎯 Project Goals

Build and deploy production-ready Pashto language models for:

- **🎓 Pashto Tutor Bot** - Educational assistance in Pashto
- **💬 Chat & Reasoning Assistant** - Conversational AI for Pashto speakers  
- **📄 Business Automation** - Document generation, summarization, form filling
- **🌍 Cultural Preservation** - Afghan culture and Islamic content
- **📚 Language Learning** - Pashto language education tools

## 📊 Dataset Overview

### 💎 High-Quality Instruction Dataset
Our curated dataset contains **137 high-quality examples** for fine-tuning:

| Category | Examples | Description |
|----------|----------|-------------|
| 🎓 Tutor Chat | 46 | Educational Q&A and tutoring |
| 📰 News Summarization | 72 | Text summarization from news articles |
| 💼 Business Automation | 4 | Business letters, forms, documents |
| 🏛️ Cultural Content | 4 | Afghan traditions and customs |
| ☪️ Islamic Content | 3 | Religious guidance and teachings |
| 🗣️ Language Learning | 5 | Conversational practice |
| 🤔 General Q&A | 3 | General knowledge |

### 🗂️ Big Data Archives (730K+ Documents)
We also provide massive raw datasets for base model training:

| Archive | Size | Documents | Content | Year |
|---------|------|-----------|---------|------|
| **Pashto News 2020** | ~2.5GB | 100,000 | News articles | 2020 |
| **Pashto Web Crawl** | ~2.2GB | 100,000 | Web content | 2011 |
| **Pashto Wikipedia** | ~800MB | 30,000 | Encyclopedia | 2021 |
| **Text Corpus** | ~1.2GB | 500K+ | Mixed content | Various |

**Total Raw Data: 6.7GB+ with 730,000+ documents**

## 🚀 Quick Start

### 1. Setup Environment

```bash
git clone https://github.com/tasal9/Pashto-Dataset-Creating-Dataset.git
cd Pashto-Dataset-Creating-Dataset
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python zamai_training_dataset.py
```

### 3. Train Your Model

```bash
python zamai_model_trainer.py --mode train \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --dataset_path zamai_final_dataset/zamai_training_dataset.jsonl \
  --hub_model_id tasal9/zamai-tutor-v1
```

### 4. Deploy Interface

```bash
python app.py
```

## 📁 Repository Structure

```
├── 📂 zamai_final_dataset/           # Generated training datasets
│   ├── zamai_training_dataset.jsonl  # Main training file (HuggingFace format)
│   ├── zamai_training_dataset.json   # JSON format
│   ├── zamai_training_dataset.csv    # CSV format
│   └── dataset_info.json             # Dataset metadata
├── 📂 Pashto-Data/                   # Raw data sources
│   ├── gathered_data/                # Scraped news articles
│   ├── pashto-text-dataset/          # Text corpus
│   └── Pashto_High_value_dataset/    # Metadata files
├── 🐍 zamai_training_dataset.py      # Dataset creation script
├── 🤖 zamai_model_trainer.py         # Model training script
├── 🌐 app.py                         # Gradio web interface
├── 📋 requirements.txt               # Python dependencies
├── 📖 IMPLEMENTATION_GUIDE.md        # Detailed implementation guide
└── 📝 zamai_text_strategy.md         # Original strategy document
```

## 🎯 Use Cases & Examples

### Educational Tutor
```python
instruction = "د ریاضیاتو بنسټیز مفاهیم راته وروښیه"
response = "د ریاضیاتو بنسټیز مفاهیم پدې دي: شمېرنه (۱، ۲، ۳...)، جمع کول (+)، لرې کول (-)..."
```

### Cultural Assistant
```python
instruction = "د افغانستان دودیز خواړه کوم دي؟"
response = "د افغانستان دودیز خواړه پدې دي: پلاو، کباب، مانتو، بولاني، قورمه..."
```

### Business Automation
```python
instruction = "د سوداګرۍ خط راته ولیکه"
response = "درناوي ملګري، موږ ستاسو ته زموږ د نوي محصول په اړه خبر ورکوو..."
```

## 🧠 Supported Models

The dataset works with multiple transformer architectures:

| Model | Best For | Size | Performance |
|-------|----------|------|-------------|
| **Mistral-7B-Instruct** | Chat & Reasoning | 7B | ⭐⭐⭐⭐⭐ |
| **Phi-3-mini** | Tutor Bot | 3.8B | ⭐⭐⭐⭐ |
| **Llama-3-8B** | Summarization | 8B | ⭐⭐⭐⭐⭐ |
| **Gemma-7B** | General Purpose | 7B | ⭐⭐⭐⭐ |

## 🌐 Deployment Options

### HuggingFace Spaces (Recommended)
```bash
# Deploy instantly to HF Spaces
huggingface-cli upload app.py tasal9/zamai-pashto-assistant --repo-type space
```

### Local Gradio Interface
```bash
python zamai_model_trainer.py --mode gradio
```

## 📚 Documentation

- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Detailed setup and training instructions
- **[Strategy Document](zamai_text_strategy.md)** - Original ZamAI text-first approach

## 🌟 Key Features

✅ **High-Quality Data**: Manually curated and validated Pashto content  
✅ **Multiple Formats**: JSONL, JSON, and CSV support  
✅ **Category-Specific**: Organized by use case and domain  
✅ **HuggingFace Ready**: Compatible with transformers library  
✅ **Gradio Interface**: Ready-to-deploy web interface  
✅ **Cultural Authenticity**: Native Afghan perspective  
✅ **Islamic Compliance**: Respectful religious content  
✅ **Educational Focus**: Strong pedagogical foundation  

## 🤝 Contributing

We welcome contributions to expand and improve the dataset:

1. **Add New Categories**: Healthcare, Legal, Technical domains
2. **Expand Existing Data**: More examples in current categories  
3. **Quality Improvements**: Better responses and instructions
4. **Multilingual Support**: Add Dari and English translations
5. **Evaluation Tools**: Better metrics and benchmarks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**ZamAI Team** - Building the future of Pashto AI

## 📞 Support & Contact

- **GitHub Issues**: [Create an issue](https://github.com/tasal9/Pashto-Dataset-Creating-Dataset/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tasal9/Pashto-Dataset-Creating-Dataset/discussions)

---

**د پښتو ژبې پرمختګ ته ونډه اخیستل - Contributing to Pashto Language Development** 🇦🇫

Made with ❤️ for the Afghan community and Pashto language preservation.
Follow the repository’s file structure.
License
This repository is licensed under the MIT License, unless otherwise stated for individual datasets.
Please see dataset-specific README files for additional licensing terms.

Contact
For questions, suggestions, or collaboration, please use GitHub Issues.
