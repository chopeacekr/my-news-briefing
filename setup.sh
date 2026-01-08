#!/bin/bash

# ArXiv-NewsBrief v4.0 Chatbot Setup & Run Script

echo "================================"
echo "ArXiv-NewsBrief v4.0 Setup"
echo "================================"

# Step 1: UV 프로젝트 초기화 (이미 있다면 스킵)
if [ ! -f "pyproject.toml" ]; then
    echo "📦 Initializing UV project..."
    uv init
else
    echo "✅ pyproject.toml already exists"
fi

# Step 2: 필요한 패키지 설치
echo ""
echo "📦 Installing dependencies..."

uv add streamlit
uv add gtts
uv add pydub
uv add SpeechRecognition
uv add langchain-google-genai
uv add torch
uv add transformers
uv add peft
uv add bitsandbytes
uv add accelerate

echo ""
echo "✅ Package installation complete!"

# Step 3: 모델 경로 확인
echo ""
echo "================================"
echo "Model Path Check"
echo "================================"

if [ -d "ArXiv-NewsBrief-1.5B-1k-v4.0/final_model" ]; then
    echo "✅ v4.0 model found: ArXiv-NewsBrief-1.5B-1k-v4.0/final_model"
    ls -la ArXiv-NewsBrief-1.5B-1k-v4.0/final_model
else
    echo "⚠️  v4.0 model NOT found!"
    echo "Please ensure the model is in: ArXiv-NewsBrief-1.5B-1k-v4.0/final_model"
    echo ""
    echo "Expected files:"
    echo "  - adapter_config.json"
    echo "  - adapter_model.safetensors (or .bin)"
    echo "  - config.json"
    echo "  - tokenizer files"
fi

# Step 4: 실행 안내
echo ""
echo "================================"
echo "Ready to Run!"
echo "================================"
echo ""
echo "To start the chatbot:"
echo "  uv run streamlit run arxiv_chatbot.py"
echo ""
echo "Or manually:"
echo "  uv run python -m streamlit run arxiv_chatbot.py"
echo ""
echo "================================"