# WeWork Chatbot - Gemini Version

This folder contains the Google Gemini powered version of the WeWork customer service chatbot with advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Conda (recommended)
- Google Gemini API Key

### 1. Setup Environment
```bash
# Create conda environment
conda create -n wework-gemini python=3.9
conda activate wework-gemini

# Install dependencies
cd RAG
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# Or paste it when prompted by the application
```

### 3. Start the Backend
```bash
cd RAG
python flask_api.py
```
The RAG API will start on `http://localhost:5000`

### 4. Start the Frontend
```bash
# In a new terminal
cd Chatbot_UI
python3 server.py
```
The chatbot UI will start on `http://localhost:8080`

### 5. Test the Chatbot
Open `http://localhost:8080` in your browser and ask questions like:
- "What is a Private Office?"
- "How many WeWork centers are in India?"
- "Tell me about booking policies"

## 📁 Folder Structure

```
WeWork_Chatbot_Gemini/
├── RAG/
│   ├── optimized_rag.py              # Core RAG system
│   ├── flask_api.py                  # Gemini API wrapper
│   ├── complete_gemini_prompt.py     # Gemini-optimized prompt
│   ├── requirements.txt              # Python dependencies
│   ├── cache/                        # ChromaDB vector database
│   └── Enhanced_Json_KB/             # Knowledge base files
├── Chatbot_UI/
│   ├── index.html                   # Main chatbot interface
│   ├── styles.css                   # UI styling
│   ├── script.js                    # Frontend JavaScript
│   └── server.py                    # Simple HTTP server
└── README.md                        # This file
```

## 🔧 Configuration

### Model Settings
- **LLM**: Google Gemini Pro (via Google AI API)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: ChromaDB
- **Retrieval**: Multi-step retrieval with query expansion

### API Endpoints
- `POST /chat` - Main chatbot endpoint
- `GET /health` - Health check
- `GET /status` - System status
- `POST /rebuild` - Rebuild knowledge base

## 🎯 Features

- **Advanced RAG**: Multi-step retrieval with abbreviation detection
- **WeWork Knowledge**: Comprehensive FAQ database
- **Smart Responses**: Context-aware answers with links
- **Security**: Jailbreak protection and content filtering
- **UI/UX**: Modern floating chatbot interface
- **Gemini Optimized**: Prompts specifically tuned for Gemini's behavior

## 🛠 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade sentence-transformers transformers tokenizers
   ```

2. **Gemini API Issues**
   - Verify your API key is set correctly
   - Check your Google AI Studio account

3. **Port Already in Use**
   ```bash
   # Kill existing processes
   pkill -f flask_api.py
   pkill -f server.py
   ```

4. **Vector Database Issues**
   ```bash
   # Rebuild the knowledge base
   curl -X POST http://localhost:5000/rebuild
   ```

5. **Greeting Issues**
   - Gemini uses a specialized prompt structure for better instruction following
   - Responses are optimized to avoid unnecessary greetings

## 📊 Performance

- **Response Time**: ~1-2 seconds
- **Knowledge Base**: 14 comprehensive FAQ files
- **Accuracy**: Optimized for WeWork-specific queries with Gemini-tuned prompts
- **Concurrency**: Supports multiple simultaneous users

## 🔄 Switching to GPT-4o

If you want to use GPT-4o instead, check out the `WeWork_Chatbot_GPT4o` folder for the OpenAI GPT-4o powered version.

## 🤝 Contributing

1. Test your changes thoroughly
2. Update documentation if needed
3. Follow the existing code style
4. Ensure API compatibility

## 📝 License

Internal WeWork project - Not for public distribution.

## 📂 Using Shared Data (Recommended)

By default, this version will look for a shared knowledge base at `../../data/files` and URLs at `../../data/url_files/urls.txt`.

- Override paths with environment variables:
  ```bash
  export WEWORK_DATA_DIR="../../data/files"
  export WEWORK_URLS_FILE="../../data/url_files/urls.txt"
  ```

- If you change the data, rebuild vectors:
  ```bash
  curl -X POST http://localhost:5000/rebuild
  # or delete the cache folder and restart
  rm -rf RAG/cache/*
  ```
