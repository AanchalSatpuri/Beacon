#!/usr/bin/env python3
"""
Flask API for WeWork Optimized RAG System
Provides REST API endpoints for the WeWork chatbot UI integration.
"""

import os
import logging
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import RAG components
from optimized_rag import initialize_rag_system, query_rag_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Global state
rag_initialized = False
rag_lock = threading.Lock()

def init_rag():
    """Initialize RAG system in background thread."""
    global rag_initialized
    with rag_lock:
        if not rag_initialized:
            logger.info("Initializing optimized RAG system...")
            try:
                initialize_rag_system()
                rag_initialized = True
                logger.info("✅ Optimized RAG system initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize RAG system: {e}", exc_info=True)
                rag_initialized = False

# Start RAG initialization in background
threading.Thread(target=init_rag, daemon=True).start()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "WeWork RAG API",
        "rag_initialized": rag_initialized
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Detailed status endpoint."""
    api_key_configured = bool(os.getenv("GEMINI_API_KEY"))
    
    return jsonify({
        "service": "WeWork Optimized RAG API",
        "rag_initialized": rag_initialized,
        "ready_for_queries": rag_initialized and api_key_configured,
        "api_key_configured": api_key_configured
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Process chatbot queries using the optimized RAG system."""
    if not rag_initialized:
        return jsonify({
            "error": "RAG system not initialized yet. Please wait.",
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
        logger.info(f"Processing query: '{query}' (membership: {data.get('membership_type', 'General')})")
        
        response_text = query_rag_system(query)
        
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.2f} seconds")
        
        return jsonify({
            "response": response_text,
            "success": True,
            "metadata": {
                "processing_time": round(processing_time, 2),
                "query_length": len(query),
                "response_length": len(response_text),
                "membership_type": data.get('membership_type', 'General')
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
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
        initialize_rag_system()
        rag_initialized = True
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
    print("🚀 WeWork Optimized RAG API Server")
    print("=" * 60)
    print(f"✅ RAG system initialized: {rag_initialized}")
    print("📡 API Endpoints:")
    print("  • POST /chat        - Process chatbot queries")
    print("  • GET  /health      - Health check")
    print("  • GET  /status      - System status")
    print("  • POST /rebuild     - Rebuild knowledge base")
    print("🌐 Starting server on http://localhost:5000")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)

if __name__ == '__main__':
    print_startup_message()
    app.run(host='0.0.0.0', port=5000, debug=False)