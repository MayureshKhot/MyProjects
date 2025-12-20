import streamlit as st
import os
import re
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

# --- Page Configuration ---
st.set_page_config(page_title="RAG-Bot", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for a Polished, Dark Look ---
st.markdown("""
<style>
    /* --- CSS VARIABLES FOR EASY THEMEING --- */
    :root {
        --dark-bg: #111827;         /* Dark blue-grey background */
        --component-bg: #1F2937;    /* Lighter grey for components */
        --border-color: #374151;    /* Subtle border color */
        --primary-text: #F9FAFB;    /* Off-white for main text */
        --secondary-text: #9CA3AF;  /* Lighter grey for subtitles */
        --accent-color: #8B5CF6;    /* Vibrant violet */
        --accent-hover: #A78BFA;    /* Lighter violet for hover */
        --error-color: #EF4444;     /* Red for errors */
        --success-color: #10B981;   /* Green for success */
        --warning-color: #F59E0B;   /* Amber for warnings */
    }

    /* General App Styling */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--primary-text);
        font-family: 'Inter', sans-serif; /* A clean, modern font */
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar Styling */
    .stSidebar {
        background-color: var(--component-bg);
        border-right: 1px solid var(--border-color);
    }
    .stSidebar h2, .stSidebar h3 {
        color: var(--primary-text);
        font-weight: 600;
    }

    /* Button Styling */
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.25);
    }
    .stButton>button:hover {
        background-color: var(--accent-hover);
        box-shadow: 0 6px 20px 0 rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
    }
    .stButton>button:active {
        background-color: var(--accent-color);
        transform: translateY(0);
    }

    /* Input Fields */
    .stTextInput>div>div>input, .st-emotion-cache-1g8i8d4>div>div>input {
        background-color: var(--component-bg);
        color: var(--primary-text);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.4);
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed var(--accent-color);
        border-radius: 8px;
        background-color: rgba(139, 92, 246, 0.05); /* Subtle accent tint */
        padding: 1.5rem;
    }
    
    /* Main Title */
    .main-title {
        color: #FFFFFF;
        text-align: center;
        font-weight: 700;
        padding-bottom: 10px;
        text-shadow: 0 0 8px rgba(139, 92, 246, 0.5); /* Cool glow effect */
    }
    
    /* Subtitle / Intro Text */
    .intro-text {
        text-align: center;
        color: var(--secondary-text);
        font-size: 1.1rem;
        padding-bottom: 2rem;
    }
    
    /* Expander for Source Docs */
    .stExpander {
        background-color: var(--component-bg);
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }

    /* --- ALERT/STATUS BOXES --- */
    [data-testid="stAlert"] {
        border-radius: 8px;
        border: none;
        background-color: var(--component-bg);
        border-left: 5px solid var(--secondary-text);
    }
    [data-testid="stAlert"][data-baseweb="notification-positive"] {
        border-left-color: var(--success-color);
        background-color: rgba(16, 185, 129, 0.1);
    }
    [data-testid="stAlert"][data-baseweb="notification-negative"] {
        border-left-color: var(--error-color);
        background-color: rgba(239, 68, 68, 0.1);
    }
    [data-testid="stAlert"][data-baseweb="notification-warning"] {
        border-left-color: var(--warning-color);
        background-color: rgba(245, 158, 11, 0.1);
    }
    
    /* --- CHAT MESSAGES --- */
    [data-testid="stChatMessage"] {
        background-color: var(--component-bg);
        border-radius: 10px;
        padding: 1rem 1.25rem;
    }
    
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None


# --- Helper Functions (Backend Logic) ---

def get_pdf_text(pdf_docs):
    """Extracts text from a list of uploaded PDF files."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def get_text_chunks(text):
    """Splits text into manageable chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Creates and stores a vector store from text chunks."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        st.session_state.vector_store = vector_store
        st.sidebar.success("✅ Documents processed successfully!")
    except Exception as e:
        st.sidebar.error(f"Embedding Error: {e}")

def get_conversational_chain():
    """Creates the conversational retrieval chain with a custom prompt."""
    
    # Updated prompt to handle LaTeX formula rendering
    prompt_template = """
    You are an AI assistant. Your primary goal is to answer questions based on the provided documents.

    1. First, search the 'Context' section below for the answer. If you find it, answer the user's question clearly and concisely using only that information.
    2. If the answer is not in the context, evaluate if the user's 'Question' is still related to the topics discussed in the context.
    3. If it is related, you may use your own knowledge to provide a helpful answer. However, you MUST start your response with the exact phrase: "The document do not contain the context about your query, but here's what might help..."
    4. If the question is completely unrelated to the context, simply state that you cannot find the answer in the provided documents.
    5. Do not invent or assume details beyond what is given in the context unless you are following rule #3.
    6. **IMPORTANT**: When you include a mathematical formula, you MUST enclose it in double dollar signs ($$) for it to render correctly. For example: $$E = mc^2$$

    Context:  
    {context}  

    Question:  
    {question}  

    Answer:
    """
    
    llm = ChatGroq(api_key=st.session_state.groq_api_key, model="openai/gpt-oss-120b")
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=st.session_state.vector_store.as_retriever(),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return chain

# --- UI Rendering ---

def main():
    """Main function to render the Streamlit UI."""
    # --- Sidebar ---
    with st.sidebar:
        st.header("Setup")

        st.session_state.groq_api_key = st.text_input(
            "Enter your Groq API Key:", type="password", key="groq_key"
        )
        st.markdown("---")

        st.header("Your Documents")
        pdf_docs = st.file_uploader(
            "Upload PDFs and click 'Process'",
            accept_multiple_files=True,
            type="pdf"
        )

        if st.button("Process Documents"):
            if not pdf_docs:
                st.warning("Please upload at least one PDF file.")
            elif not st.session_state.get("groq_api_key"):
                st.warning("Please enter your Groq API key to proceed.")
            else:
                with st.spinner("Processing documents... this may take a moment."):
                    raw_text = get_pdf_text(pdf_docs)
                    if not raw_text.strip():
                        st.error("Could not extract text from the PDF(s). Please check the files and try again.")
                    else:
                        text_chunks = get_text_chunks(raw_text)
                        get_vector_store(text_chunks)

    # --- Main Chat Interface ---
    st.markdown("<h1 class='main-title'>RAG-Bot: Your Personal Document Assistant 💬</h1>", unsafe_allow_html=True)
    st.markdown("<p class='intro-text'>Upload your documents, ask questions, and get answers grounded in their content.</p>", unsafe_allow_html=True)

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for prerequisites before generating a response
        if st.session_state.vector_store is None:
            st.warning("Please process your documents before asking questions.")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I'm ready to help, but you need to upload and process your documents first in the sidebar!"
            })
            st.rerun()

        if not st.session_state.get("groq_api_key"):
            st.warning("Please enter your Groq API key in the sidebar.")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can't connect to my brain! Please provide a Groq API key in the sidebar."
            })
            st.rerun()

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                chain = get_conversational_chain()
                response = chain.invoke({"query": prompt}) # Use invoke for newer LangChain versions
                answer = response["result"]
                
                # Clean the answer by removing the <think> tag block
                answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()

                st.markdown(answer)

                # Display source documents in an expander (dropdown)
                with st.expander("🔍 See the sources behind the story"):
                    for i, doc in enumerate(response["source_documents"]):
                        st.info(f"Source {i+1}:\n\n---\n\n{doc.page_content}")
                        
            except Exception as e:
                error_message = f"An error occurred: {e}"
                st.error(error_message)
                answer = "I seem to have encountered a glitch. Please check the sidebar for any warnings or try your question again."
        
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()





