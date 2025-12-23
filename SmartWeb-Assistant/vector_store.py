import os
import glob
import logging
import torch
import time
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

# Configure logging
logger = logging.getLogger(__name__)

def load_documents(data_dir):
    documents = []
    for file_path in glob.glob(os.path.join(data_dir, '*.txt')):
        loader = TextLoader(file_path, encoding='utf-8')
        documents.extend(loader.load())
    return documents

def create_vector_store(data_dir):
    documents = load_documents(data_dir)
    if not documents:
        logger.error("No documents found in scraped_data folder")
        return None
    logger.info(f"Loaded {len(documents)} documents")
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        logger.error("QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        return None
    
    timestamp = int(time.time())
    collection_name = f"website_data_{timestamp}"
    
    logger.info("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    
    logger.info("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': "cpu"}
    )
    
    logger.info("Creating Qdrant vector store...")
    try:
        vector_store = Qdrant.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name=collection_name,
            force_recreate=True,
            timeout=420
        )
        logger.info("Vector store created successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        return None

def get_existing_vector_store(collection_name):
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        logger.error("QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        return None
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': "cpu"}
    )
    
    try:
        vector_store = Qdrant(
            client=QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            ),
            collection_name=collection_name,
            embeddings=embeddings
        )
        logger.info(f"Loaded existing vector store: {collection_name}")
        return vector_store
    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}")
        return None
