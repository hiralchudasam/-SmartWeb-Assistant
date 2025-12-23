import os
import time
import glob
import logging
import streamlit as st
import warnings
from dotenv import load_dotenv

from web_crawler import WebCrawlerURLs
from web_scraper import scrape_website, clear_scraped_data
from vector_store import create_vector_store, get_existing_vector_store
from rag_system import setup_rag_chain, log_qa_interaction
from chat_history_db import ChatHistoryDB
from ui_components import setup_ui, display_message, create_sidebar, is_valid_url

# Suppress warnings
warnings.filterwarnings('ignore')
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="rag_system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Initialize chat history database
chat_db = ChatHistoryDB()

# Constants
DATA_DIR = "data"
URL_FILE = os.path.join(DATA_DIR, "crawled_urls.txt")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped_data")

def initialize_session_state():
    """Initialize session state variables."""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'success_messages' not in st.session_state:
        st.session_state.success_messages = []
    if 'current_website' not in st.session_state:
        st.session_state.current_website = None

def process_website(website_url):
    """Process a website for the RAG system."""
    st.session_state.success_messages = []
    st.session_state.current_website = website_url
    
    # Check if website is already processed
    existing_collection = chat_db.get_qdrant_collection(website_url)
    
    if existing_collection:
        st.session_state.success_messages.append("Website already processed. Loading from Qdrant...")
        vector_store = get_existing_vector_store(existing_collection)
        
        if vector_store:
            st.session_state.vector_store = vector_store
            st.session_state.qa_chain = setup_rag_chain(vector_store)
            st.session_state.messages = [{
                'role': 'assistant',
                'content': "Website loaded from Qdrant! I'm ready to answer questions about the website. Ask me anything!"
            }]
            st.session_state.success_messages.append("Vector store loaded successfully. You can now use the chat.")
            return True
        else:
            st.error("Failed to load vector store from Qdrant.")
            return False
    else:
        # New website processing
        st.session_state.success_messages.append("New website detected. Starting processing...")
        
        # Clear any existing scraped data
        clear_scraped_data(SCRAPED_DIR)
        
        # Crawl website URLs
        with st.spinner("Fetching webpage URLs..."):
            crawler = WebCrawlerURLs(website_url, URL_FILE)
            crawler.crawl_urls()
            crawler.save_urls_to_file()
            st.session_state.success_messages.append(f"Fetched {len(crawler.all_urls)} URLs.")
        
        # Scrape website content
        with st.spinner("Scraping website content..."):
            scrape_website(URL_FILE, SCRAPED_DIR)
            st.session_state.success_messages.append("Website content scraped successfully.")
        
        # Create vector store
        with st.spinner("Creating vector store..."):
            timestamp = int(time.time())
            collection_name = f"website_data_{timestamp}"
            vector_store = create_vector_store(SCRAPED_DIR)
            
            if vector_store:
                chat_db.save_qdrant_collection(website_url, collection_name)
                st.session_state.vector_store = vector_store
                st.session_state.qa_chain = setup_rag_chain(vector_store)
                st.session_state.messages = [{
                    'role': 'assistant',
                    'content': "Website processed successfully! I'm ready to answer questions about the website. Ask me anything!"
                }]
                st.session_state.success_messages.append("Vector store created successfully. You can now use the chat.")
                return True
            else:
                st.error("Failed to create vector store.")
                return False

def main():
    # Setup UI components
    setup_ui()
    
    # Initialize session state
    initialize_session_state()
    
    # Ensure data directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SCRAPED_DIR, exist_ok=True)
    
    # Create sidebar with website input
    website_url, process_button = create_sidebar()
    
    # Process website if button is clicked
    if process_button:
        if not website_url:
            st.error("Please enter a valid URL.")
        elif not is_valid_url(website_url):
            st.error("Invalid URL format. Please enter a valid URL starting with http:// or https://")
        else:
            try:
                process_website(website_url)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error in processing: {str(e)}")
    
    # Display success messages
    for message in st.session_state.success_messages:
        st.sidebar.success(message)
    
    # Main chat interface
    st.header("Website Assistant")
    
    if not st.session_state.vector_store:
        st.warning("Please process a website in the sidebar before using the chat.")
    else:
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                display_message(message['content'], message['role'] == 'user')
        
        # Chat input
        if prompt := st.chat_input("Ask about the website..."):
            st.session_state.messages.append({'role': 'user', 'content': prompt})
            with chat_container:
                display_message(prompt, is_user=True)
            
            try:
                with st.spinner("Generating response..."):
                    response = st.session_state.qa_chain({"query": prompt})
                    answer = response["result"]
                    st.session_state.messages.append({'role': 'assistant', 'content': answer})
                    with chat_container:
                        display_message(answer, is_user=False)
                    
                    if st.session_state.current_website:
                        chat_db.save_chat(st.session_state.current_website, prompt, answer)
                    
                    log_qa_interaction(prompt, answer, response["source_documents"])
            except Exception as e:
                logger.error(f"Error in QA: {str(e)}")
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': "I apologize, but I encountered an error. Please try again."
                })
                with chat_container:
                    display_message("I apologize, but I encountered an error. Please try again.", is_user=False)

if __name__ == "__main__":
    main()
    chat_db.close()
