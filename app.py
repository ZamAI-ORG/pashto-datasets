#!/usr/bin/env python3
"""
ZamAI Gradio App for HuggingFace Spaces

This is the main application file for deploying ZamAI Pashto Assistant
to HuggingFace Spaces.

Author: ZamAI Team
Date: June 30, 2025
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os
import logging
from typing import List, Tuple, Optional
import json
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZamAIPashtoAssistant:
    """ZamAI Pashto Language Assistant"""
    
    def __init__(self, model_name: str = "tasal9/zamai-tutor-v1"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.conversation_history = []
        
    def load_model(self):
        """Load the model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_response(self, 
                         message: str, 
                         max_new_tokens: int = 256,
                         temperature: float = 0.7,
                         top_p: float = 0.95) -> str:
        """Generate response for user message"""
        
        if not self.pipeline:
            if not self.load_model():
                return "د موډل د لوډولو کې ستونزه شته. بخښنه غواړم!"
        
        try:
            # Format the prompt
            prompt = f"<s>[INST] {message} [/INST]"
            
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            # Extract response
            response = outputs[0]["generated_text"].strip()
            
            # Clean up response
            if response.startswith("[/INST]"):
                response = response[7:].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "بخښنه غواړم، ما د دې ته ځواب ورکولو کې ستونزه درلوده. لطفاً بیا هڅه وکړئ."
    
    def chat_interface(self, message: str, history: List[Tuple[str, str]]) -> str:
        """Main chat interface function for Gradio"""
        response = self.generate_response(message)
        return response

# Initialize the assistant
assistant = ZamAIPashtoAssistant()

# Pre-defined examples and information
EXAMPLES = [
    "د افغانستان پایتخت چه شی دی؟",
    "د پښتو ژبې زده کړه څنګه پیل کړم؟", 
    "د اسلام د پنځو ستنو په اړه راته ووایه",
    "د افغانستان دودیز خواړه کوم دي؟",
    "د ریاضیاتو بنسټیز مفاهیم راته وروښیه",
    "د روغتیا د ساتلو لپاره څه وکړم؟",
    "د پښتنو دودونه او رواجونه راته ووایه",
    "د انګلیسي ژبې زده کړه څنګه پیل کړم؟"
]

ABOUT_TEXT = """
# 🇦🇫 ZamAI - د پښتو ژبې ذکي مرستیال

**ZamAI** د پښتو ژبې لپاره یو پرمختللی ذکي مرستیال دی چې د Hugging Face په پلیټ فارم کې جوړ شوی.

## 🎯 ځانګړتیاوې

- **د پښتو ژبې ملاتړ**: دا مرستیال په بشپړ ډول د پښتو ژبې ملاتړ کوي
- **تعلیمي مرستې**: د ښوونې او روزنې لپاره ډیزاین شوی
- **کلتوري پوښتنې**: د افغان کلتور او دودونو په اړه معلومات
- **اسلامي معلومات**: د اسلامي تعلیماتو په اړه رهنمایي
- **عمومي پوښتنې**: د ورځني ژوند د ستونزو حل

## 🚀 د کارونې لارښوونه

1. خپله پوښتنه د پښتو ژبې کې ولیکئ
2. د مثالونو څخه یو ټاکئ یا خپله پوښتنه ولیکئ
3. د ځواب انتظار وکړئ

## 📝 د کارونې مثالونه

- تعلیمي پوښتنې: "د ریاضیاتو بنسټیز مفاهیم راته وروښیه"
- کلتوري پوښتنې: "د افغانستان دودیز خواړه کوم دي؟"
- اسلامي پوښتنې: "د اسلام د پنځو ستنو په اړه راته ووایه"
- ژبنۍ مرستې: "د پښتو ژبې زده کړه څنګه پیل کړم؟"

---
*د ZamAI ټیم لخوا جوړ شوی | Made by ZamAI Team*
"""

# Custom CSS for better RTL support
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');

.gradio-container {
    font-family: 'Noto Sans Arabic', Arial, sans-serif !important;
    direction: rtl;
}

.message {
    direction: rtl !important;
    text-align: right !important;
}

.user-message {
    background-color: #E3F2FD !important;
    direction: rtl !important;
    text-align: right !important;
    border-radius: 15px !important;
    padding: 10px !important;
    margin: 5px !important;
}

.bot-message {
    background-color: #F1F8E9 !important;
    direction: rtl !important;
    text-align: right !important;
    border-radius: 15px !important;
    padding: 10px !important;
    margin: 5px !important;
}

.chat-input {
    direction: rtl !important;
    text-align: right !important;
}

.examples {
    direction: rtl !important;
    text-align: right !important;
}

.title {
    text-align: center !important;
    color: #1976D2 !important;
    font-weight: bold !important;
}

.description {
    direction: rtl !important;
    text-align: right !important;
    color: #424242 !important;
}
</style>
"""

def create_interface():
    """Create the main Gradio interface"""
    
    # Create the chat interface
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green"
        ),
        css=CUSTOM_CSS,
        title="ZamAI - د پښتو ژبې ذکي مرستیال"
    ) as app:
        
        # Header
        gr.HTML("""
        <div class="title">
            <h1>🇦🇫 ZamAI - د پښتو ژبې ذکي مرستیال</h1>
            <h3>Intelligent Pashto Language Assistant</h3>
        </div>
        """)
        
        # Main chat interface
        chatbot = gr.Chatbot(
            height=400,
            show_label=False,
            container=True,
            bubble_full_width=False
        )
        
        with gr.Row():
            with gr.Column(scale=4):
                msg = gr.Textbox(
                    label="خپله پوښتنه دلته ولیکئ / Enter your question here",
                    placeholder="د پښتو ژبې کې خپله پوښتنه ولیکئ...",
                    lines=2,
                    container=True
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("ولیږه / Send", variant="primary", size="lg")
                clear_btn = gr.Button("پاک کړه / Clear", variant="secondary", size="lg")
        
        # Examples
        gr.Examples(
            examples=EXAMPLES,
            inputs=msg,
            label="د مثالونو څخه یو ټاکئ / Choose an example:",
        )
        
        # Advanced settings
        with gr.Accordion("د پرمختللو تنظیماتو / Advanced Settings", open=False):
            with gr.Row():
                max_tokens = gr.Slider(
                    minimum=50,
                    maximum=512,
                    value=256,
                    step=10,
                    label="د ځواب اوږدوالی / Response Length"
                )
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=1.5,
                    value=0.7,
                    step=0.1,
                    label="د تنوع کچه / Creativity Level"
                )
        
        # About section
        with gr.Accordion("د ZamAI په اړه / About ZamAI", open=False):
            gr.Markdown(ABOUT_TEXT)
        
        # Event handlers
        def respond(message, chat_history, max_tokens, temperature):
            if not message.strip():
                return "", chat_history
            
            # Generate response
            response = assistant.generate_response(
                message, 
                max_new_tokens=int(max_tokens),
                temperature=temperature
            )
            
            # Update chat history
            chat_history.append((message, response))
            
            return "", chat_history
        
        def clear_chat():
            return [], ""
        
        # Connect events
        submit_btn.click(
            respond,
            inputs=[msg, chatbot, max_tokens, temperature],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            respond,
            inputs=[msg, chatbot, max_tokens, temperature],
            outputs=[msg, chatbot]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, msg]
        )
    
    return app

# Create and launch the app
if __name__ == "__main__":
    app = create_interface()
    
    # Launch configuration
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        quiet=False
    )
