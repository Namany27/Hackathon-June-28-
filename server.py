from modal import App, Image, asgi_app, Secret
from fastapi import FastAPI, Request
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from huggingface_hub import login
import re

# Model info
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

# Define Modal app
app = App("course-crafter-mistral-server")

# Define Modal image with dependencies
image = (
    Image.from_registry("pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime")
    .pip_install(
        "transformers==4.40.0",
        "torch",
        "accelerate",
        "fastapi",
        "uvicorn",
        "huggingface_hub"
    )
)

# Helper to clean LLaMA output
def clean_llama_response(decoded: str, original_prompt: str) -> str:
    for tag in ["<s>", "</s>", "<|begin_of_text|>", "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>", "[/", "[/SYS]", "SYS]", "<<INST>]", "<|eot_id|>"]:
        decoded = decoded.replace(tag, "")
    decoded = decoded.strip()

    if original_prompt.strip() in decoded:
        decoded = decoded.split(original_prompt.strip(), 1)[-1].strip()

# Remove the fixed system message and the user's query block (case-insensitive, multiline, dot matches newline)
    decoded = re.sub(
        r"You are a helpful assistant.*?I want to learn.*?/SYS", "", decoded, flags=re.DOTALL | re.IGNORECASE
)

# Then find and trim from roadmap-related intro phrases
    match = re.search(r"(?i)(here'?s|i'?ve|this\s+roadmap|month\s+1|step\s+1|week\s+1|let'?s\s+start)", decoded)
    if match:
        decoded = decoded[match.start():].strip()
     
    return decoded

# Create FastAPI instance
web_app = FastAPI()

# Define Modal function as ASGI app
@app.function(
    image=image,
    secrets=[Secret.from_name("huggingface-token")],
    timeout=600,
    min_containers=1, 
    max_containers=20,
    cpu=4,
    memory="16Gi",
    gpu="A100-40GB"
)
@asgi_app()
def fastapi_app():
    login(os.environ["HUGGINGFACE_HUB_TOKEN"])

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        use_auth_token=True
    )

    @web_app.post("/v18/chat/completions")
    async def chat_endpoint(request: Request):
        payload = await request.json()
        messages = payload.get("messages", [])

        # Construct prompt
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<<SYS>>\n{content}\n<</SYS>>\n"
            elif role == "user":
                prompt += f"{content.strip()}\n"
            elif role == "assistant":
                prompt += f"{content.strip()}\n"

        final_prompt = f"<s>[INST] {prompt.strip()} [/INST]"

        # Tokenize and generate
        inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode and clean
        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=False).strip()
        cleaned = clean_llama_response(decoded, prompt)
        print(cleaned)

        # Format response
        return {
            "id": "chatcmpl-modal",
            "object": "chat.completion",
            "model": MODEL_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": cleaned},
                    "finish_reason": "stop",
                }
            ],
        }

    return web_app