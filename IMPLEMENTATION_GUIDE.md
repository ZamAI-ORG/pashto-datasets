# 🇦🇫 ZamAI Pashto Dataset - Complete Implementation Guide

This guide provides step-by-step instructions to implement the ZamAI text strategy using the created high-quality Pashto dataset.

## 📊 Dataset Overview

**Total Examples**: 137  
**Categories**:
- **Tutor Chat**: 46 examples (educational Q&A)
- **News Summarization**: 72 examples (text summarization)  
- **Business Automation**: 4 examples (forms, letters)
- **Cultural Content**: 4 examples (Afghan culture)
- **Islamic Content**: 3 examples (religious guidance)
- **Language Learning**: 5 examples (conversation)
- **General Q&A**: 3 examples (knowledge base)

## 🚀 Quick Start Implementation

### Step 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/tasal9/Pashto-Dataset-Creating-Dataset.git
cd Pashto-Dataset-Creating-Dataset

# Install dependencies
pip install -r requirements.txt

# Login to HuggingFace
huggingface-cli login
```

### Step 2: Upload Dataset to HuggingFace Hub

```bash
# Upload as private dataset
huggingface-cli upload-dataset zamai_final_dataset/ tasal9/zamai-pashto-dataset --private
```

### Step 3: Fine-tune Models

#### Option A: Chat Assistant (Mistral-7B)
```bash
python zamai_model_trainer.py \
  --mode train \
  --model_name mistralai/Mistral-7B-Instruct-v0.2 \
  --dataset_path zamai_final_dataset/zamai_training_dataset.jsonl \
  --output_dir ./zamai-chat-v1 \
  --hub_model_id tasal9/zamai-chat-v1
```

#### Option B: Tutor Bot (Phi-3-mini)
```bash
python zamai_model_trainer.py \
  --mode train \
  --model_name microsoft/Phi-3-mini-4k-instruct \
  --dataset_path zamai_final_dataset/zamai_training_dataset.jsonl \
  --output_dir ./zamai-tutor-v1 \
  --hub_model_id tasal9/zamai-tutor-v1
```

#### Option C: Summarization (Llama-3-8B)
```bash
python zamai_model_trainer.py \
  --mode train \
  --model_name meta-llama/Meta-Llama-3-8B-Instruct \
  --dataset_path zamai_final_dataset/zamai_training_dataset.jsonl \
  --output_dir ./zamai-summarizer-v1 \
  --hub_model_id tasal9/zamai-summarizer-v1
```

### Step 4: Deploy to HuggingFace Spaces

1. Create a new Space on HuggingFace Hub
2. Upload the `app.py` file 
3. Set the model name in the app configuration
4. Your Pashto assistant will be live!

## 🎯 Use Cases Implementation

### 1. Educational Tutor Bot

**Purpose**: Answering educational questions in Pashto  
**Model**: Phi-3-mini or Mistral-7B  
**Training Focus**: tutor_chat and educational categories

```python
from transformers import pipeline

# Load your fine-tuned model
generator = pipeline("text-generation", model="tasal9/zamai-tutor-v1")

# Example usage
question = "د ریاضیاتو بنسټیز مفاهیم راته وروښیه"
response = generator(f"<s>[INST] {question} [/INST]", max_new_tokens=256)
```

### 2. News Summarization

**Purpose**: Summarizing Pashto news articles  
**Model**: Any transformer model  
**Training Focus**: news_summarization category

```python
# Example summarization
text = "د افغانستان په فاریاب ولایت کې په یوه پارک کې ښځو په برقعو کې ورزش کړی دی..."
prompt = f"<s>[INST] دا متن لنډ کړه: {text} [/INST]"
summary = generator(prompt, max_new_tokens=100)
```

### 3. Business Automation

**Purpose**: Generate business documents in Pashto  
**Training Focus**: business_automation category

```python
# Generate business letter
request = "د سوداګرۍ خط راته ولیکه"
prompt = f"<s>[INST] {request} [/INST]"
letter = generator(prompt, max_new_tokens=200)
```

## 📈 Advanced Training Configuration

### Custom Training Parameters

```python
from zamai_model_trainer import ZamAITrainingConfig, ZamAIModelTrainer

config = ZamAITrainingConfig(
    model_name="mistralai/Mistral-7B-Instruct-v0.2",
    dataset_path="zamai_final_dataset/zamai_training_dataset.jsonl",
    output_dir="./zamai-custom-v1",
    num_train_epochs=5,
    per_device_train_batch_size=4,
    learning_rate=1e-5,
    max_length=1024,
    fp16=True,
    push_to_hub=True,
    hub_model_id="tasal9/zamai-custom-v1"
)

trainer = ZamAIModelTrainer(config)
trainer.train()
```

### Multi-GPU Training

```bash
# Use accelerate for multi-GPU training
accelerate config
accelerate launch zamai_model_trainer.py --mode train
```

## 🌐 Deployment Options

### Option 1: HuggingFace Spaces (Recommended)

1. Create `app.py` with the provided Gradio interface
2. Upload to HF Spaces
3. Automatic deployment and hosting

### Option 2: Local Gradio Interface

```bash
python zamai_model_trainer.py --mode gradio --output_dir ./zamai-tutor-v1
```

### Option 3: API Deployment

```python
from transformers import pipeline
from fastapi import FastAPI

app = FastAPI()
generator = pipeline("text-generation", model="tasal9/zamai-tutor-v1")

@app.post("/generate")
def generate_response(instruction: str):
    prompt = f"<s>[INST] {instruction} [/INST]"
    response = generator(prompt, max_new_tokens=256)
    return {"response": response[0]["generated_text"]}
```

## 📊 Model Evaluation

### Evaluation Script

```python
from datasets import load_dataset
from transformers import pipeline

# Load test set
test_data = load_dataset("json", data_files="zamai_final_dataset/zamai_training_dataset.jsonl", split="train")
test_data = test_data.train_test_split(test_size=0.1)["test"]

# Load model
generator = pipeline("text-generation", model="tasal9/zamai-tutor-v1")

# Evaluate
total_examples = 0
for example in test_data:
    instruction = example["instruction"]
    expected = example["response"]
    
    prompt = f"<s>[INST] {instruction} [/INST]"
    generated = generator(prompt, max_new_tokens=256)[0]["generated_text"]
    
    print(f"Question: {instruction}")
    print(f"Expected: {expected}")
    print(f"Generated: {generated}")
    print("-" * 50)
    total_examples += 1

print(f"Evaluated {total_examples} examples")
```

## 🔧 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size: `per_device_train_batch_size=1`
   - Use gradient accumulation: `gradient_accumulation_steps=8`
   - Enable gradient checkpointing: `gradient_checkpointing=True`

2. **Model Loading Issues**
   - Ensure you have access to the base model
   - Check HuggingFace token permissions
   - Verify model name spelling

3. **Pashto Text Encoding**
   - Always use UTF-8 encoding
   - Set proper RTL direction in web interfaces
   - Use appropriate fonts for Pashto text

### Performance Optimization

```python
# Optimize for inference
import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "tasal9/zamai-tutor-v1",
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_8bit=True  # For memory optimization
)
```

## 📚 Additional Resources

### Expanding the Dataset

```python
# Add more training examples
new_examples = [
    {
        "instruction": "نوې پوښتنه",
        "response": "ځواب",
        "category": "education"
    }
]

# Append to existing dataset
with open("zamai_final_dataset/zamai_training_dataset.jsonl", "a") as f:
    for example in new_examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
```

### Custom Categories

You can create domain-specific datasets by filtering categories:

```python
import json

# Load full dataset
with open("zamai_final_dataset/zamai_training_dataset.jsonl") as f:
    all_data = [json.loads(line) for line in f]

# Filter for education only
education_data = [item for item in all_data if item.get("category") == "education"]

# Save education-specific dataset
with open("education_dataset.jsonl", "w") as f:
    for item in education_data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
```

## 🎯 Next Steps

1. **Train your first model** using the provided scripts
2. **Deploy to HuggingFace Spaces** for public access
3. **Evaluate and iterate** based on user feedback
4. **Expand the dataset** with domain-specific content
5. **Build mobile apps** using the API endpoints

## 📞 Support

For questions or support:
- GitHub Issues: Create an issue in the repository
- HuggingFace Community: Post in the discussions
- Documentation: Check the README and code comments

---

**Happy Training! د زده کړې ښه پاتې شه!** 🚀
