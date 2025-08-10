# WeWork Chatbot - Quick Start Guide

Choose your preferred AI model and follow the steps below:

## 🤖 Option 1: GPT-4o Version (Recommended)

### Setup Steps:
```bash
# 1. Navigate to GPT-4o folder
cd WeWork_Chatbot_GPT4o

# 2. Create conda environment
conda create -n wework-gpt4o python=3.9
conda activate wework-gpt4o

# 3. Install dependencies
cd RAG
pip install -r requirements.txt

# 4. Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# 5. Start backend (Terminal 1)
python flask_api.py

# 6. Start frontend (Terminal 2)
cd ../Chatbot_UI
python3 server.py
```

### Access:
- **Chatbot UI**: http://localhost:8080
- **API Health**: http://localhost:5000/health

---

## 💎 Option 2: Gemini Version

### Setup Steps:
```bash
# 1. Navigate to Gemini folder
cd WeWork_Chatbot_Gemini

# 2. Create conda environment
conda create -n wework-gemini python=3.9
conda activate wework-gemini

# 3. Install dependencies
cd RAG
pip install -r requirements.txt

# 4. Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# 5. Start backend (Terminal 1)
python flask_api.py

# 6. Start frontend (Terminal 2)
cd ../Chatbot_UI
python3 server.py
```

### Access:
- **Chatbot UI**: http://localhost:8080
- **API Health**: http://localhost:5000/health

---

## 🚀 One-Command Start (Alternative)

### GPT-4o:
```bash
cd WeWork_Chatbot_GPT4o
./start_gpt4o.sh
```

### Gemini:
```bash
cd WeWork_Chatbot_Gemini
./start_gemini.sh
```

---

## 🔧 API Keys

### Get OpenAI API Key:
1. Go to https://platform.openai.com/api-keys
2. Create new key
3. Copy and use in OPENAI_API_KEY

### Get Gemini API Key:
1. Go to https://makersuite.google.com/app/apikey
2. Create new key
3. Copy and use in GEMINI_API_KEY

---

## ✅ Test Queries

Try these questions:
- "What is a Private Office?"
- "How many WeWork centers are in India?"
- "Tell me about booking policies"
- "What are the payment options?"

---

## 🛑 Stop Servers

Press `Ctrl+C` in both terminal windows or:
```bash
pkill -f flask_api.py
pkill -f server.py
```
