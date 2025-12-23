
# 💬 RAG-Powered Website Chatbot

A full-stack, real-time chatbot application that leverages Retrieval-Augmented Generation (RAG) with LangChain and LLaMA 3 to provide accurate, source-backed answers from live website content.

## 🚀 Features

- 🔍 **Web Crawling & Scraping**: Fetches and cleans content from entire websites using rotating proxies.
- 🧠 **Retrieval-Augmented Generation**: Employs a LLaMA 3 model integrated via LangChain to provide context-aware answers.
- 📦 **Vector Store with Qdrant**: Stores document embeddings for efficient and scalable retrieval.
- 💬 **Streamlit Chat UI**: Intuitive, real-time interface with chat history, user roles, and persistent sessions.
- 🔄 **Dynamic Content Reloading**: Supports both new and previously cached websites.
- 🗃 **Chat History Tracking**: Logs interactions in a SQLite database for future reference.

## 🛠 Architecture

```
User ↔ Streamlit UI ↔ LangChain QA Chain ↔ Qdrant Vector Store ↔ Web Scraping Pipeline
```

### Modules

- `app.py`: Main Streamlit app with session management and chat UI.
- `web_crawler.py`: Crawls and collects internal URLs.
- `web_scraper.py`: Scrapes HTML content and converts it to markdown.
- `vector_store.py`: Handles embedding creation and Qdrant vector store integration.
- `rag_system.py`: Sets up LangChain RAG chain using LLaMA 3 with custom prompts.
- `chat_history_db.py`: Manages chat and website metadata persistence via SQLite.
- `ui_components.py`: Handles all UI/UX components using Streamlit.

## 📦 Installation

### Prerequisites

- Python 3.8+
- `.env` file with the following:
  ```env
  GROQ_API_KEY=your_groq_key
  QDRANT_URL=https://your-qdrant-instance
  QDRANT_API_KEY=your_qdrant_key
  ```

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot

# Install dependencies
pip install -r requirements.txt
```

## 🚦 Usage

```bash
streamlit run app.py
```

Enter a website URL in the sidebar to crawl, scrape, index, and interact with its content in real time.

## 📁 Data

- All processed documents are stored in `data/scraped_data`.
- URLs are tracked in `data/crawled_urls.txt`.
- Chat history is stored in `chat_history.db`.

## 🧪 Technologies

- **LangChain**
- **LLaMA 3 via GROQ API**
- **Qdrant**
- **Streamlit**
- **SQLite**
- **BeautifulSoup**
- **html2text**

