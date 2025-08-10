from langchain_community.document_loaders import (
    TextLoader,
)
import PyPDF2
import docx2txt
import json
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv("api_key.env")
load_dotenv(".env")
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not set. "
        "Please copy env.example to api_key.env and add your API key. "
        "Get one at: https://makersuite.google.com/app/apikey"
    )

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Cache paths - Updated for local environment
CACHE_DIR = './cache'
os.makedirs(CACHE_DIR, exist_ok=True)
DOCS_CACHE = os.path.join(CACHE_DIR, 'documents.pkl')
WEB_CACHE = os.path.join(CACHE_DIR, 'web_documents.pkl')
SCRAPE_WEB = False  # Disabled for local testing

# OPTIMIZED EMBEDDING MODELS FOR DIFFERENT USE CASES
EMBEDDING_OPTIONS = {
    "qa_optimized": "sentence-transformers/multi-qa-mpnet-base-dot-v1",  # Best for Q&A
    "retrieval_optimized": "sentence-transformers/msmarco-mpnet-base-v3",  # Best for retrieval
    "general_fast": "sentence-transformers/all-MiniLM-L6-v2",  # Fast and good
    "general_best": "sentence-transformers/all-mpnet-base-v2",  # Current default
    "paraphrase": "sentence-transformers/paraphrase-mpnet-base-v2",  # Good for similar meaning
}

# Choose the best model for Q&A tasks
SELECTED_MODEL = "general_fast"  # Using faster model to avoid torch.distributed issues

print(f"🚀 Using embedding model: {EMBEDDING_OPTIONS[SELECTED_MODEL]}")
print("Loading embedding model...")
start_time = time.time()
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_OPTIONS[SELECTED_MODEL],
    model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU available
    encode_kwargs={'normalize_embeddings': True}  # Normalize for better similarity scores
)
print(f"Model loaded in {time.time() - start_time:.2f} seconds")

def extract_potential_abbreviations(query: str) -> list:
    """Extract potential abbreviations from query."""
    potential_abbrevs = re.findall(r'\b[a-zA-Z]{1,4}\b', query.lower())
    known_abbreviations = ['po', 'aa', 'vo', 'od', 'mo', 'wwl', 'wws', 'wbs', 'aappu', 'aaplus']
    found_abbrevs = [abbrev for abbrev in potential_abbrevs if abbrev in known_abbreviations]
    return found_abbrevs

def search_for_abbreviation_definitions(retriever, abbreviations: list):
    """Search for abbreviation definitions with optimized queries."""
    print(f"🔍 Step 1: Searching for abbreviation definitions for: {abbreviations}")
    
    abbreviation_chunks = []
    
    # More targeted queries for better retrieval
    abbrev_queries = [
        "WeWork product abbreviations list definitions",
        "Private Office PO abbreviation meaning", 
        "List of WeWork product abbreviations",
        "abbreviations WeWork services",
        f"{' '.join(abbreviations)} abbreviation definition"
    ]
    
    for query in abbrev_queries:
        chunks = retriever.invoke(query)
        abbreviation_chunks.extend(chunks)
    
    # Remove duplicates
    seen_content = set()
    unique_abbrev_chunks = []
    for chunk in abbreviation_chunks:
        content_hash = hash(chunk.page_content[:100])
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_abbrev_chunks.append(chunk)
    
    print(f"   Found {len(unique_abbrev_chunks)} abbreviation definition chunks")
    return unique_abbrev_chunks

def extract_abbreviation_mappings(abbreviation_chunks: list, target_abbrevs: list) -> dict:
    """Extract abbreviation mappings with improved pattern matching."""
    print(f"🔍 Step 2: Extracting abbreviation mappings for: {target_abbrevs}")
    
    mappings = {}
    
    for chunk in abbreviation_chunks:
        content = chunk.page_content.lower()
        
        # Enhanced pattern matching
        for abbrev in target_abbrevs:
            if abbrev in content:
                # Look for various patterns
                patterns = [
                    f"{abbrev}.*private office",
                    f"private office.*{abbrev}",
                    f"{abbrev}.*all access plus", 
                    f"all access plus.*{abbrev}",
                    f"{abbrev}.*virtual office",
                    f"virtual office.*{abbrev}",
                    f"{abbrev}.*on-demand",
                    f"on-demand.*{abbrev}"
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        if 'private office' in pattern:
                            mappings[abbrev] = 'Private Office'
                        elif 'all access plus' in pattern:
                            mappings[abbrev] = 'All Access Plus'
                        elif 'virtual office' in pattern:
                            mappings[abbrev] = 'Virtual Office'
                        elif 'on-demand' in pattern:
                            mappings[abbrev] = 'On-demand'
                        break
    
    print(f"   Extracted mappings: {mappings}")
    return mappings

def expand_query_with_mappings(original_query: str, mappings: dict) -> str:
    """Expand query with better context preservation."""
    expanded_query = original_query
    
    for abbrev, full_form in mappings.items():
        # Replace abbreviation but also add full form for better retrieval
        pattern = r'\b' + abbrev + r'\b'
        replacement = f"{abbrev} {full_form}"  # Keep both for better matching
        expanded_query = re.sub(pattern, replacement, expanded_query, flags=re.IGNORECASE)
    
    print(f"🔍 Step 3: Expanded query: '{original_query}' → '{expanded_query}'")
    return expanded_query

def multi_step_retrieve(retriever, query: str, k: int = 8):
    """Optimized multi-step retrieval process."""
    print(f"\n🚀 MULTI-STEP RETRIEVAL for: '{query}'")
    print("="*60)
    
    all_chunks = []
    
    # Step 1: Extract potential abbreviations
    abbreviations = extract_potential_abbreviations(query)
    
    if abbreviations:
        print(f"✓ Found potential abbreviations: {abbreviations}")
        
        # Step 2: Search for abbreviation definitions with higher k for better coverage
        abbrev_chunks = search_for_abbreviation_definitions(retriever, abbreviations)
        
        # Add best abbreviation chunks
        best_abbrev_chunks = sorted(abbrev_chunks, 
                                   key=lambda x: x.page_content.lower().count('abbreviation') + 
                                               x.page_content.lower().count('private office'))[:3]
        all_chunks.extend(best_abbrev_chunks)
        
        # Step 3: Extract mappings
        mappings = extract_abbreviation_mappings(abbrev_chunks, abbreviations)
        
        if mappings:
            # Step 4: Search with expanded query
            expanded_query = expand_query_with_mappings(query, mappings)
            expanded_chunks = retriever.invoke(expanded_query)
            all_chunks.extend(expanded_chunks[:4])
            
            # Step 5: Also search with just the full forms for more coverage
            for abbrev, full_form in mappings.items():
                full_form_query = query.replace(abbrev, full_form)
                if full_form_query != expanded_query:  # Avoid duplicates
                    additional_chunks = retriever.invoke(full_form_query)
                    all_chunks.extend(additional_chunks[:2])
        else:
            print("⚠️  No abbreviation mappings found, using original query")
            original_chunks = retriever.invoke(query)
            all_chunks.extend(original_chunks[:4])
    else:
        print("ℹ️  No abbreviations detected, using standard retrieval")
        original_chunks = retriever.invoke(query)
        all_chunks.extend(original_chunks[:k])
    
    # Step 6: Smart deduplication and ranking
    seen_content = set()
    unique_chunks = []
    
    for chunk in all_chunks:
        content_hash = hash(chunk.page_content[:100])
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_chunks.append(chunk)
    
    # Rank chunks by relevance to query
    def relevance_score(chunk, query_words):
        content = chunk.page_content.lower()
        score = sum(1 for word in query_words if word in content)
        # Bonus for abbreviation definitions
        if 'abbreviation' in content or 'private office -' in content:
            score += 2
        return score
    
    query_words = query.lower().split()
    unique_chunks.sort(key=lambda x: relevance_score(x, query_words), reverse=True)
    
    final_chunks = unique_chunks[:k]
    print(f"🎯 Final result: {len(final_chunks)} unique chunks")
    print("="*60)
    
    return final_chunks

def generate_answer_with_gemini(question: str, context_chunks: list) -> str:
    """Generate answer with complete Gemini-optimized WeWork prompt including all original features."""
    from complete_gemini_prompt import get_complete_gemini_prompt
    
    chunks_retrieved = "\n\n".join([f"Chunk {i+1}:\n{chunk.page_content}" 
                                   for i, chunk in enumerate(context_chunks)])
    
    prompt = get_complete_gemini_prompt(question, chunks_retrieved)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def load_local_files():
    """Load local files from WeWork data directory."""
    print("Loading local files...")
    start_time = time.time()

    if os.path.exists(DOCS_CACHE):
        with open(DOCS_CACHE, 'rb') as f:
            pages = pickle.load(f)
        print(f"Loaded {len(pages)} documents from cache in {time.time() - start_time:.2f} seconds")
        return pages

    # Updated for local environment
    UPLOAD_FOLDER = './files/'
    pages = []

    if not os.path.exists(UPLOAD_FOLDER):
        print(f"Warning: {UPLOAD_FOLDER} not found. Creating empty list.")
        return []

    for file in tqdm(os.listdir(UPLOAD_FOLDER), desc="Processing local files"):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        try:
            if file.endswith('.pdf'):
                # Use PyPDF2 for PDF files
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    pages.append(Document(page_content=text, metadata={"source": file_path}))
            elif file.endswith('.docx') or file.endswith('.doc'):
                # Use docx2txt for Word documents
                text = docx2txt.process(file_path)
                pages.append(Document(page_content=text, metadata={"source": file_path}))
            elif file.endswith('.txt'):
                # Use TextLoader for text files
                loader = TextLoader(file_path)
                pages.extend(loader.load())
            elif file.endswith('.json'):
                # Handle JSON files manually
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    text = json.dumps(data, indent=2)
                    pages.append(Document(page_content=text, metadata={"source": file_path}))
        except Exception as e:
            print(f"Error loading {file}: {e}")

    with open(DOCS_CACHE, 'wb') as f:
        pickle.dump(pages, f)

    print(f"Processed {len(pages)} documents in {time.time() - start_time:.2f} seconds")
    return pages

def fetch_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            try:
                page.goto(url, timeout=15000)
                page.wait_for_load_state('domcontentloaded', timeout=15000)
                return page.content()
            except Exception as e:
                print(f"Error loading page for {url}: {e}")
                return None
            finally:
                page.close()
        except Exception as e:
            print(f"Browser error for {url}: {e}")
            return None
        finally:
            browser.close()

def load_url_with_playwright(url: str) -> list[Document]:
    html = fetch_rendered_html(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return [Document(page_content=text, metadata={"source": url})]

def load_web_documents():
    print("Loading web documents...")
    start_time = time.time()

    if not SCRAPE_WEB:
        print("Web scraping disabled. Skipping...")
        return []

    if os.path.exists(WEB_CACHE):
        with open(WEB_CACHE, 'rb') as f:
            web_docs = pickle.load(f)
        print(f"Loaded {len(web_docs)} web documents from cache in {time.time() - start_time:.2f} seconds")
        return web_docs

    URL_FILE = './url_files/urls.txt'

    if not os.path.exists(URL_FILE):
        print(f"Warning: {URL_FILE} not found. Skipping web documents.")
        return []

    with open(URL_FILE, 'r') as f:
        web_urls = f.read().splitlines()

    print(f"Scraping {len(web_urls)} URLs...")

    def fetch_and_process_url(url):
        try:
            return load_url_with_playwright(url)
        except Exception as e:
            print(f"Failed to load {url}: {e}")
            return []

    web_docs = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = list(tqdm(executor.map(fetch_and_process_url, web_urls), total=len(web_urls), desc="Scraping websites"))
        for docs in futures:
            web_docs.extend(docs)

    with open(WEB_CACHE, 'wb') as f:
        pickle.dump(web_docs, f)

    print(f"Processed {len(web_docs)} web documents in {time.time() - start_time:.2f} seconds")
    return web_docs

# Global variables for the RAG system
vectorstore = None
retriever = None

def initialize_rag_system():
    """Initialize the RAG system once and keep it in memory."""
    global vectorstore, retriever
    
    if vectorstore is not None and retriever is not None:
        print("RAG system already initialized.")
        return
    
    print("Initializing RAG system...")
    start_time = time.time()
    
    local_docs = load_local_files()
    web_docs = load_web_documents()
    pages = local_docs + web_docs

    flat_pages = []
    for page in tqdm(pages, desc="Flattening documents"):
        if isinstance(page, list):
            flat_pages.extend(page)
        else:
            flat_pages.append(page)

    print(f"Total documents to process: {len(flat_pages)}")

    # Use model-specific persist directory to avoid conflicts
    PERSIST_DIR = os.path.join(CACHE_DIR, f'chroma_{SELECTED_MODEL}')

    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print(f"Loading Chroma vectorstore from disk ({SELECTED_MODEL})...")
        vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_model)
    else:
        print("Creating text chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        split_docs = text_splitter.split_documents(flat_pages)
        print(f"Created {len(split_docs)} chunks")

        print(f"Creating new Chroma vectorstore with {SELECTED_MODEL}...")
        vectorstore = Chroma.from_documents(split_docs, embedding=embedding_model, persist_directory=PERSIST_DIR)
        vectorstore.persist()

    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})  # Increased k for better coverage
    
    print(f"RAG system initialized in {time.time() - start_time:.2f} seconds")

def query_rag_system(question: str) -> str:
    """Query the RAG system with a question."""
    global retriever
    
    if retriever is None:
        initialize_rag_system()
    
    try:
        chunks = multi_step_retrieve(retriever, question)
        answer = generate_answer_with_gemini(question, chunks)
        return answer
    except Exception as e:
        return f"Error processing question: {str(e)}"

def main():
    """Main function for testing the RAG system."""
    initialize_rag_system()
    
    questions = [
        "what is po",
        "discount on all access plus",
        "what is the price of private office"
    ]

    print("\n" + "="*80)
    print(f"OPTIMIZED RAG SYSTEM - MODEL: {EMBEDDING_OPTIONS[SELECTED_MODEL]}")
    print("="*80)

    for question in questions:
        print(f"\n🎯 Question: {question}")
        print("-" * 60)
        
        answer = query_rag_system(question)
        print(f"\n🤖 Answer: {answer}")
        print("\n" + "="*80)

    # Interactive mode
    print("\n🎮 INTERACTIVE MODE (OPTIMIZED EMBEDDINGS)")
    print("="*50)
    print(f"Using: {EMBEDDING_OPTIONS[SELECTED_MODEL]}")
    print("Ask your own questions! (type 'quit' to exit)")
    
    while True:
        user_question = input("\nYour question: ").strip()
        
        if user_question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not user_question:
            continue
        
        answer = query_rag_system(user_question)
        print(f"\n💡 Answer: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    main()
