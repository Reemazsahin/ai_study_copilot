# 📚 AI Study Copilot

I'm Reemaz Sahin, a CSE (AIML) student. I built this project because I always 
wanted a tool that could actually help me study smarter not just search through 
a PDF, but actually understand it, quiz me, and guide my thinking.
So I built one.

# Why I Built This

Studying from long PDFs is painful. You read 50 pages and forget half of it.
I wanted a tool that could:
- Answer my questions from the PDF
- Quiz me automatically
- Help me think (not just memorize)
- Let me take a proper timed exam

# What It Can Do 

 💬 Chat with PDF - Ask anything from your PDF and get a clear answer|
 📝 Quiz Generator - Creates MCQ questions automatically from your PDF| 
 🃏 Flashcards - Flip cards for quick last minute revision|
 📋 Summarizer - Breaks down the whole PDF into key points| 
 🧠 Socratic Tutor - Asks YOU questions instead of giving answers directly|
 📊 Exam Simulator - Timed exam with scoring, grades and answer review|
 🎤 Voice Input - Record your question and upload — no typing needed|
 📂 Multi PDF - Upload multiple PDFs and ask across all of them|

# Tech Stack

 Streamlit - Quick to build, looks clean, easy to deploy|
 Groq + LLaMA 3.3 70B - Fast and free LLM API|
 FAISS - Stores PDF chunks as vectors for fast search| 
 SentenceTransformers - Converts text to embeddings locally| 
 LangChain - Handles text splitting and RAG pipeline|
 PyMuPDF - Extracts text from PDF files|
 FFmpeg + SpeechRecognition - Handles voice input transcription. 

# How the RAG Pipeline Works

Upload PDF
->
Extract text (PyMuPDF)
->
Split into chunks (LangChain)
->
Convert to embeddings (SentenceTransformers)
->
Store in FAISS vector database
->
User asks question
->
Find similar chunks (FAISS search)
->
Send chunks + question to Groq LLM
->
Show answer to user

# Hardest Part

The voice input feature was the most frustrating part.

I couldn't get PyAudio to install on Windows at all — it kept failing no matter 
what I tried. I ended up using FFmpeg directly with subprocess to convert audio 
files to WAV format, then used SpeechRecognition to transcribe them.It took a lot of debugging but it finally worked!

# How to Run This Project

## 1.Clone the repo
```bash
git clone https://github.com/Reemazsahin/ai_study_copilot.git
cd ai_study_copilot
```

## 2.Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

## 3.Install dependencies
```bash
pip install -r requirements.txt
```

## 4.Add your Groq API key
Create a `.env` file: GROQ_API_KEY=your_key_here
Get your free key at → https://console.groq.com

## 5.Run it
```bash
streamlit run app.py
```

# Project Structure
ai_study_copilot/

├── app.py              # Main app — all 7 tabs live here

├── llm_handler.py      # All Groq LLM calls — answers, quiz, flashcards etc

├── vector_store.py     # FAISS setup and similarity search

├── pdf_utils.py        # PDF text extraction

├── voice_utils.py      # Audio conversion and transcription

├── requirements.txt    # Dependencies

└── .env                # Your API key 

# What I Learned

- How RAG pipeline actually works end to end
- How vector databases store and search text
- How to connect a local embedding model with FAISS
- How to handle audio transcription without PyAudio on Windows
- How to manage Streamlit session state across multiple tabs
- How to balance token limits when sending chunks to an LLM