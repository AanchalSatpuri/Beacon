#!/usr/bin/env python3
"""
Flask API for WeWork Chatbot using GPT-4o instead of Gemini
Provides REST API endpoints for the WeWork chatbot UI integration with GPT-4o.
"""

import os
import logging
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# Import RAG components
from optimized_rag import initialize_rag_system, multi_step_retrieve
from wework_prompt import get_wework_prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None

# Global state
rag_initialized = False
rag_lock = threading.Lock()
retriever = None

def initialize_openai():
    """Initialize OpenAI client"""
    global openai_client
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return False

def query_with_gpt4o(question: str, context_chunks: list) -> str:
    """Query GPT-4o with the WeWork prompt"""
    
    chunks_retrieved = "\n\n".join([f"Chunk {i+1}:\n{chunk.page_content}" 
                                   for i, chunk in enumerate(context_chunks)])
    
    prompt = get_wework_prompt(question, chunks_retrieved)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful WeWork customer service assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with GPT-4o: {str(e)}"

def init_rag():
    """Initialize RAG system in background thread."""
    global rag_initialized, retriever
    with rag_lock:
        if not rag_initialized:
            logger.info("Initializing RAG system for GPT-4o...")
            try:
                initialize_rag_system()
                
                # Get the retriever from the module
                from optimized_rag import retriever as rag_retriever
                retriever = rag_retriever
                
                rag_initialized = True
                logger.info("✅ RAG system initialized successfully for GPT-4o")
            except Exception as e:
                logger.error(f"❌ Failed to initialize RAG system: {e}", exc_info=True)
                rag_initialized = False

# Initialize OpenAI and RAG system
if initialize_openai():
    threading.Thread(target=init_rag, daemon=True).start()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "WeWork GPT-4o API",
        "rag_initialized": rag_initialized,
        "openai_initialized": openai_client is not None
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Detailed status endpoint."""
    return jsonify({
        "service": "WeWork GPT-4o RAG API",
        "rag_initialized": rag_initialized,
        "openai_initialized": openai_client is not None,
        "ready_for_queries": rag_initialized and openai_client is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Process chatbot queries using GPT-4o."""
    if not rag_initialized:
        return jsonify({
            "error": "RAG system not initialized yet. Please wait.",
            "success": False
        }), 503
        
    if not openai_client:
        return jsonify({
            "error": "OpenAI client not initialized",
            "success": False
        }), 503
        
    data = request.json
    query = data.get('query') or data.get('message')
    
    if not query:
        return jsonify({
            "error": "No query provided",
            "success": False
        }), 400
        
    try:
        start_time = time.time()
        logger.info(f"Processing query with GPT-4o: '{query}' (membership: {data.get('membership_type', 'General')})")
        
        # Get relevant chunks using RAG retrieval
        context_chunks = multi_step_retrieve(retriever, query, k=8)
        
        # Query GPT-4o
        response_text = query_with_gpt4o(query, context_chunks)
        
        processing_time = time.time() - start_time
        logger.info(f"GPT-4o query processed in {processing_time:.2f} seconds")
        
        return jsonify({
            "response": response_text,
            "success": True,
            "metadata": {
                "processing_time": round(processing_time, 2),
                "query_length": len(query),
                "response_length": len(response_text),
                "membership_type": data.get('membership_type', 'General'),
                "model": "gpt-4o"
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing chat query with GPT-4o: {e}", exc_info=True)
        return jsonify({
            "error": f"Internal server error: {e}",
            "response": "I apologize, but I encountered an error while processing your question. Please try rephrasing your question or contact support.",
            "success": False
        }), 500

@app.route('/rebuild', methods=['POST'])
def rebuild_knowledge_base():
    """Rebuild the knowledge base."""
    global rag_initialized
    logger.info("Rebuild request received. Reinitializing RAG system...")
    rag_initialized = False
    
    try:
        # Clear cache
        import shutil
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            logger.info(f"Cleared cache directory: {cache_dir}")
        
        # Reinitialize
        init_rag()
        logger.info("✅ Knowledge base rebuilt successfully via API.")
        
        return jsonify({
            "message": "Knowledge base rebuilt successfully",
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}", exc_info=True)
        return jsonify({
            "error": f"Failed to rebuild index: {e}",
            "success": False
        }), 500

def print_startup_message():
    """Print formatted startup message."""
    print("=" * 60)
    print("🚀 WeWork GPT-4o RAG API Server")
    print("=" * 60)
    print(f"✅ RAG system initialized: {rag_initialized}")
    print(f"✅ OpenAI client ready: {openai_client is not None}")
    print("📡 API Endpoints:")
    print("  • POST /chat        - Process chatbot queries with GPT-4o")
    print("  • GET  /health      - Health check")
    print("  • GET  /status      - System status")
    print("  • POST /rebuild     - Rebuild knowledge base")
    print("🌐 Starting server on http://localhost:5000")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)

if __name__ == '__main__':
    print_startup_message()
    app.run(host='0.0.0.0', port=5000, debug=False)
