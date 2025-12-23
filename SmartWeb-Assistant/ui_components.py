import streamlit as st
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def setup_ui():
    st.markdown("""
    <style>
        .stApp {
            background-color: #1a1a1a;
            color: #e0e0e0;
            font-family: 'Söhne', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: none !important;
            gap: 2rem;
            padding: 0 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            color: #8e8ea0;
            font-weight: 500;
            background-color: transparent !important;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #2a2a2a !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #10a37f;
            background-color: #2a2a2a !important;
            border-bottom: none !important;
        }
        .stChatInput {
            position: fixed;
            bottom: 1rem;
            left: 0;
            right: 0;
            max-width: 70%;
            margin: 0 auto;
            padding: 0.5rem;    
            z-index: 1000;
        }
        .stChatInput > div > input {
            color: #e0e0e0 !important;
        }
        .stChatMessage {
            max-width: 70%;
            padding: 0.8rem 1.2rem;
            margin-bottom: 2rem;
            border-radius: 0.8rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            clear: both;
            overflow: auto;
            word-wrap: break-word;
        }
        .stChatMessage[data-testid="stChatMessage-User"] {
            background-color: #10a37f;
            color: #ffffff;
            margin-left: auto;
            float: right;
            display: flex;
            justify-content: flex-end;
        }
        .stChatMessage[data-testid="stChatMessage-Assistant"] {
            background-color: #252525;
            color: #e0e0e0;
            margin-right: auto;
            float: left;
            display: flex;
            justify-content: flex-start;
        }
        .block-container {
            padding-bottom: 120px !important;
        }
        .main .block-container {
            padding-bottom: 120px !important;
        }
        h1, h2, h3 {
            color: #e0e0e0;
            margin-bottom: 0rem !important;
        }
        h2 {
            margin-bottom: 2rem !important;
        }
        .stTextInput > label {
            color: #e0e0e0;
        }
        .stButton > button {
            background-color: #10a37f !important;
            color: #ffffff !important;
            border: 1px solid #3a3a3a;
            border-radius: 0.4rem;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def display_message(message, is_user=False):
    avatar = "👤" if is_user else "🤖"
    message_class = "user-message" if is_user else "assistant-message"
    
    message_html = f"""
        <div class="stChatMessage" data-testid="stChatMessage-{'User' if is_user else 'Assistant'}">
            <div class="avatar">{avatar}</div>
            <div class="message-content">{message}</div>
        </div>
    """
    st.markdown(message_html, unsafe_allow_html=True)

def create_sidebar():
    with st.sidebar:
        st.header("Process Website")
        website_url = st.text_input("Enter Website URL (e.g., https://example.com)", key="website_url")
        
        if website_url and not is_valid_url(website_url):
            st.warning("Please enter a valid URL starting with http:// or https://")
        
        process_button = st.button("Submit")
        
        return website_url, process_button
