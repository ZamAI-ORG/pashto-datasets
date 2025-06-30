**ZamAI Phase 1: Text-First Strategy using Hugging Face Pro**

---

## 📅 GOAL

Build, fine-tune, and deploy text-based models for:

- Pashto tutor bot
- Chat & reasoning assistant
- Business automation (summarization, form filling, document QA)

---

## 🔧 STEP 1: Environment Setup

**Tools Required:**

- Hugging Face Pro account
- Python environment (install: `transformers`, `datasets`, `accelerate`, `huggingface_hub`)
- (Optional) GitHub repo for CI/CD

---

## 📚 STEP 2: Private Dataset Creation

Prepare datasets in JSONL or CSV like:

```json
{
  "instruction": "د افغانستان پایتخت چه شی دی؟",
  "response": "د افغانستان پایتخت کابل دی."
}
```

Upload securely using:

```bash
huggingface-cli login
datasets-cli upload ./zamai_text_data --private
```

---

## 🧬 STEP 3: Model Fine-tuning

Choose model based on task:

| Task               | Model                                        |
| ------------------ | -------------------------------------------- |
| Chat / Reasoning   | `mistralai/Mistral-7B-Instruct-v0.2`         |
| Tutor Bot          | `meta-llama/Meta-Llama-3-8B` or `Phi-3-mini` |
| Summarization / QA | `Phi-3-mini-128k-instruct`                   |

Sample Training Code:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

model_id = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Format dataset and tokenize here

training_args = TrainingArguments(
    output_dir="./zamai-finetune",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
)

trainer.train()
```

---

## 🚀 STEP 4: Deploy to HF Hub

Push model to private repo:

```bash
huggingface-cli repo create zamai-tutor-v1 --private
huggingface-cli upload ./zamai-finetune tasal9/zamai-tutor-v1
```

---

## 🌐 STEP 5: Inference Endpoint

Sample usage code:

```python
from huggingface_hub import InferenceClient

client = InferenceClient(model="tasal9/zamai-tutor-v1", token="HF_PRO_TOKEN")

resp = client.text_generation(prompt="د ازموینو تیاری چنگه ونیول شي؟", max_new_tokens=300)
print(resp)
```

---

## 📊 STEP 6: Optional MVP via Spaces

Use Gradio for test UI:

```python
import gradio as gr

def tutor_response(prompt):
    return client.text_generation(prompt=prompt, max_new_tokens=256)

gr.Interface(fn=tutor_response, inputs="text", outputs="text").launch()
```

---

## 🔍 STEP 7: Monitor & Iterate

- Use HF model evaluation tools for benchmarking
- Track usage and prompts via HF Spaces Analytics
- Build CI/CD with GitHub for auto-deploys

---

## 🚀 Summary:

- Start with tutor/chat/QA bots
- Fine-tune open models on private Pashto datasets
- Deploy with Inference API
- Test using Spaces
- Scale based on usage and feedback

