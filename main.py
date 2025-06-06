import streamlit as st
import os
import tempfile
import hashlib
import requests
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM

# ---------- Load API Keys ----------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------- Constants ----------
CHROMA_DIR = "chroma_store"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------- Custom Gemini LLM ----------
class GeminiLLM(LLM):
    def _call(self, prompt: str, stop=None, run_manager=None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise ValueError(f"❌ Gemini API Error: {response.text}")

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    @property
    def _llm_type(self) -> str:
        return "gemini-2.0-flash"

# ---------- Hashing for Cache ----------
def get_pdf_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# ---------- PDF Processor ----------
@st.cache_resource(show_spinner=True)
def process_pdf(pdf_path):
    pdf_hash = get_pdf_hash(pdf_path)
    persist_path = f"{CHROMA_DIR}/{pdf_hash}"

    if os.path.exists(persist_path):
        return Chroma(persist_directory=persist_path, embedding_function=embeddings)

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    db = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_path)
    db.persist()
    return db

# ---------- Embeddings ----------
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# ---------- Answer Generator ----------
def get_answer(db, question):
    retriever = db.as_retriever()
    llm = GeminiLLM()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain.run(question)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="📄 Resume Q&A Bot", layout="centered")
st.title("💼 Resume/Report Chatbot using Gemini AI")

uploaded_pdf = st.file_uploader("📤 Upload a PDF (resume/report)", type="pdf")

if uploaded_pdf:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    with st.spinner("🔍 Processing PDF..."):
        try:
            db = process_pdf(tmp_path)
            st.success("✅ PDF processed and ready!")
        except Exception as e:
            st.error(f"Error while processing PDF: {str(e)}")

    question = st.text_input("💬 Ask a question about your PDF:")
    if question:
        with st.spinner("🤖 Thinking..."):
            try:
                answer = get_answer(db, question)
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
