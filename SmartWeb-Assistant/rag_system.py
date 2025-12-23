import os
import logging
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configure logging
logger = logging.getLogger(__name__)

def setup_rag_chain(vector_store):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        return None
    
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.7
    )
    
    prompt_template = """You are a helpful AI assistant for our website. Your knowledge comes from the website's content that has been provided to you. Your role is to help users find information quickly without them having to search through the website manually.

    Please answer the question based on the website content provided in the context below. If the website content doesn't contain enough information to answer the question, respond with: "I apologize, but the website doesn't contain enough information to answer this question."

    Remember:
    - Only use information from the website content provided
    - Be friendly and professional in your responses
    - Never make up or infer information not present in the website content
    - If information is incomplete or unclear, say so directly
    - Focus on providing accurate and relevant information from the processed content

    Website Content Context:
    {context}

    User Question: {question}

    Assistant: """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={
            "prompt": PROMPT,
            "document_variable_name": "context"
        },
        return_source_documents=True
    )

def log_qa_interaction(question, answer, sources):
    logger.info(f"Question: {question}")
    logger.info(f"Answer: {answer}")
    logger.info("Sources:")
    for doc in sources:
        source = doc.metadata.get('source', 'Unknown source')
        logger.info(f"- {source}")
    logger.info("")
