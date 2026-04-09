# 📄 Resume/Report Q&A Chatbot (Gemini + LangChain)

## 🚀 Overview
This project is an AI-powered chatbot that allows users to upload a PDF (such as a resume or report) and ask questions about its content. It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers instead of generic responses.

---

## ⚙️ Tech Stack

- **Frontend/UI:** Streamlit  
- **LLM API:** Google Gemini API (Gemini 1.5 Flash)  
- **Framework:** LangChain  
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)  
- **Vector Database:** Chroma  
- **Language:** Python  

---

## 🧠 How It Works (Core Logic)

1. User uploads a PDF (resume/report)
2. PDF is loaded and split into chunks
3. Each chunk is converted into embeddings
4. Embeddings are stored in a vector database (Chroma)
5. When a question is asked:
   - Relevant chunks are retrieved
   - Sent to Gemini LLM
   - Final answer is generated based on context

---

## ✨ Features

- 📄 Upload any PDF (resume, report, notes)
- 🔍 Context-aware question answering
- ⚡ Fast responses using Gemini Flash model
- 🧠 Semantic search with embeddings
- 💾 Persistent vector storage (no reprocessing)
- 🔁 Caching for better performance

---

## 📁 Project Structure
├── app.py
├── chroma_store/
├── .env
├── requirements.txt
└── README.md
