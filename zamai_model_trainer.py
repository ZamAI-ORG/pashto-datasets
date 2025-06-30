#!/usr/bin/env python3
"""
ZamAI Model Training Script

This script implements the ZamAI text strategy for fine-tuning Pashto language models
using HuggingFace Transformers. Supports multiple model types and tasks.

Author: ZamAI Team
Date: June 30, 2025
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import torch
from dataclasses import dataclass, field
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    pipeline
)
from datasets import Dataset, load_dataset
import pandas as pd
from huggingface_hub import HfApi, login
import gradio as gr

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ZamAITrainingConfig:
    """Configuration for ZamAI model training"""
    
    # Model configuration
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    model_type: str = "chat"  # chat, tutor, summarization, qa
    
    # Dataset configuration
    dataset_path: str = "zamai_final_dataset/zamai_training_dataset.jsonl"
    max_length: int = 512
    
    # Training configuration
    output_dir: str = "./zamai-tutor-v1"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    warmup_steps: int = 100
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 500
    
    # Hardware configuration
    fp16: bool = True
    gradient_checkpointing: bool = True
    dataloader_num_workers: int = 4
    
    # HuggingFace configuration
    push_to_hub: bool = True
    hub_model_id: str = "tasal9/zamai-tutor-v1"
    hub_private_repo: bool = True

class ZamAIModelTrainer:
    """Main trainer class for ZamAI models"""
    
    def __init__(self, config: ZamAITrainingConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.train_dataset = None
        self.eval_dataset = None
        
    def setup_model_and_tokenizer(self):
        """Initialize model and tokenizer"""
        logger.info(f"Loading model: {self.config.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            padding_side="left"
        )
        
        # Add special tokens if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.fp16 else torch.float32,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Resize token embeddings if necessary
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        logger.info("Model and tokenizer loaded successfully")
    
    def load_and_prepare_dataset(self):
        """Load and prepare the training dataset"""
        logger.info(f"Loading dataset from: {self.config.dataset_path}")
        
        # Load dataset
        dataset = load_dataset("json", data_files=self.config.dataset_path, split="train")
        
        # Split into train/eval
        dataset = dataset.train_test_split(test_size=0.1, shuffle=True, seed=42)
        self.train_dataset = dataset["train"]
        self.eval_dataset = dataset["test"]
        
        logger.info(f"Train examples: {len(self.train_dataset)}")
        logger.info(f"Eval examples: {len(self.eval_dataset)}")
        
        # Preprocess datasets
        self.train_dataset = self.train_dataset.map(
            self._preprocess_function,
            batched=True,
            remove_columns=self.train_dataset.column_names
        )
        
        self.eval_dataset = self.eval_dataset.map(
            self._preprocess_function,
            batched=True,
            remove_columns=self.eval_dataset.column_names
        )
        
        logger.info("Dataset preprocessing completed")
    
    def _preprocess_function(self, examples):
        """Preprocess examples for training"""
        processed_texts = []
        
        for i in range(len(examples["instruction"])):
            instruction = examples["instruction"][i]
            response = examples["response"][i]
            
            # Create conversation format
            if self.config.model_type == "chat":
                # Chat format for Mistral/Llama
                text = f"<s>[INST] {instruction} [/INST] {response} </s>"
            elif self.config.model_type == "tutor":
                # Tutor format
                text = f"### استاذ: {instruction}\n### ښوونکي: {response}\n"
            else:
                # General instruction format
                text = f"### Instruction:\n{instruction}\n\n### Response:\n{response}\n"
            
            processed_texts.append(text)
        
        # Tokenize
        tokenized = self.tokenizer(
            processed_texts,
            truncation=True,
            padding=False,
            max_length=self.config.max_length,
            return_tensors=None
        )
        
        # Add labels (same as input_ids for causal LM)
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    def setup_training_arguments(self):
        """Setup training arguments"""
        return TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=self.config.fp16,
            gradient_checkpointing=self.config.gradient_checkpointing,
            dataloader_num_workers=self.config.dataloader_num_workers,
            remove_unused_columns=False,
            report_to=["tensorboard"],
            push_to_hub=self.config.push_to_hub,
            hub_model_id=self.config.hub_model_id,
            hub_private_repo=self.config.hub_private_repo,
        )
    
    def train(self):
        """Main training function"""
        logger.info("Starting ZamAI model training...")
        
        # Setup model and tokenizer
        self.setup_model_and_tokenizer()
        
        # Load and prepare dataset
        self.load_and_prepare_dataset()
        
        # Setup data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM, not masked LM
            pad_to_multiple_of=8 if self.config.fp16 else None
        )
        
        # Setup training arguments
        training_args = self.setup_training_arguments()
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )
        
        # Start training
        logger.info("Training started...")
        trainer.train()
        
        # Save final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        # Push to hub if configured
        if self.config.push_to_hub:
            logger.info("Pushing model to HuggingFace Hub...")
            trainer.push_to_hub()
        
        logger.info("Training completed successfully!")
        
        return trainer

class ZamAIInference:
    """Inference class for trained ZamAI models"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
    def load_model(self):
        """Load the trained model for inference"""
        logger.info(f"Loading model from: {self.model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        logger.info("Model loaded successfully")
    
    def generate_response(self, instruction: str, max_new_tokens: int = 256) -> str:
        """Generate response for given instruction"""
        if not self.pipeline:
            self.load_model()
        
        # Format instruction
        prompt = f"<s>[INST] {instruction} [/INST]"
        
        # Generate response
        outputs = self.pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Extract response
        full_response = outputs[0]["generated_text"]
        response = full_response.split("[/INST]")[-1].strip()
        
        return response

def create_gradio_interface(model_path: str):
    """Create Gradio interface for the trained model"""
    
    inference = ZamAIInference(model_path)
    
    def chat_response(message, history):
        response = inference.generate_response(message)
        return response
    
    # Create Gradio interface
    interface = gr.ChatInterface(
        fn=chat_response,
        title="🇦🇫 ZamAI - Pashto Language Assistant",
        description="د پښتو ژبې ذکي مرستیال - Intelligent Pashto Language Assistant",
        examples=[
            "د افغانستان پایتخت چه شی دی؟",
            "د پښتو ژبې زده کړه څنګه پیل کړم؟",
            "د اسلام د پنځو ستنو په اړه راته ووایه",
            "د افغانستان دودیز خواړه کوم دي؟",
            "د ریاضیاتو بنسټیز مفاهیم راته وروښیه"
        ],
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .chat-message {
            direction: rtl;
            text-align: right;
        }
        """
    )
    
    return interface

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZamAI Model Training and Inference")
    parser.add_argument("--mode", choices=["train", "inference", "gradio"], 
                       default="train", help="Mode to run")
    parser.add_argument("--model_name", default="mistralai/Mistral-7B-Instruct-v0.2",
                       help="Base model name")
    parser.add_argument("--dataset_path", default="zamai_final_dataset/zamai_training_dataset.jsonl",
                       help="Path to training dataset")
    parser.add_argument("--output_dir", default="./zamai-tutor-v1",
                       help="Output directory for trained model")
    parser.add_argument("--hub_model_id", default="tasal9/zamai-tutor-v1",
                       help="HuggingFace Hub model ID")
    
    args = parser.parse_args()
    
    if args.mode == "train":
        # Training mode
        config = ZamAITrainingConfig(
            model_name=args.model_name,
            dataset_path=args.dataset_path,
            output_dir=args.output_dir,
            hub_model_id=args.hub_model_id
        )
        
        trainer = ZamAIModelTrainer(config)
        trainer.train()
        
    elif args.mode == "inference":
        # Inference mode
        inference = ZamAIInference(args.output_dir)
        
        print("ZamAI Pashto Assistant - د پښتو ژبې مرستیال")
        print("Type 'quit' to exit - د وتلو لپاره 'quit' ولیکئ")
        
        while True:
            instruction = input("\nتاسو: ")
            if instruction.lower() == 'quit':
                break
            
            response = inference.generate_response(instruction)
            print(f"مرستیال: {response}")
    
    elif args.mode == "gradio":
        # Gradio interface mode
        interface = create_gradio_interface(args.output_dir)
        interface.launch(share=True)

if __name__ == "__main__":
    main()
