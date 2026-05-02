# 🧠 AutoTests AI

> AI-powered test generator designed for language teachers

---

## 📖 About

**AutoTests AI** is a tool that allows language teachers to automatically generate language tests using AI. Teachers provide a topic or request, and the system retrieves relevant grammar and vocabulary knowledge using RAG system.

The system is built around an **agentic pipeline**: the AI first creates a plan of action, retrieves relevant content using semantic search, and then generates questions tailored to the student's proficiency level (e.g. B2).

---

## 📺 Demo

Experience **AutoTests AI** in action:

<div align="center">
  <img src="demos/videos/Demo_video.gif" width="100%" alt="AutoTests AI Demo">
  <p><i>A quick walkthrough of generating a language test from a teacher's prompt.</i></p>
</div>

---

## The problem
My sister and my mom are teachers, and I've seen how they prepare tests for their students. It takes a lot of time and is quite boring and repetitive, especially when they need to create multiple versions of the same test to prevent cheating. I realized I could help them by creating a tool that automatically generates such tests. If programmers can vibe-code and then review their code, why can't teachers vibe-create and then review tests?

---

## ✨ Features

- 🤖 AI-generated tests based on teacher prompts (topic, level, number of groups)
- 📚 RAG (Retrieval-Augmented Generation) using Qdrant vector database and sentence-transformers
- 📄 Exports tests to PDF using fpdf2
- 🌐 REST API built with FastAPI
- 🖥️ CLI interface

---

## 🚀 Quick Start — Just want to use the app?
https://auto-tests-ai-frontend-bunj.vercel.app/


---

## 🛠️ Developer Setup — Running from source

For developers who want to run or modify the project locally.

### Requirements

- Python 3.12+
- Ollama running locally or accessible via API
- Qdrant instance

### Installation

1. **Clone the repository**

```bash
git clone [https://github.com/KrzysDev/AITestGenerator.git](https://github.com/KrzysDev/AITestGenerator.git)
cd AITestGenerator
pip install -r requirements.txt
# from root directory
uvicorn backend.app.main:app --reload
python frontend/main_app.py
```

# 🗂️ Project Structure
```
  AITestGenerator/
  ├── backend/                        # Backend (FastAPI)
  │   └── app/
  │       ├── api/                    # API endpoints
  │       ├── config/                 # Configuration and language settings
  │       ├── models/                 # Data schemas and prompts
  │       ├── services/               # Business logic
  │       ├── utils/                  # Helper utilities
  │       └── main.py                 # Main application entry point
  ├── data/                           # Data files and templates
  ├── demos/                          # Media and demonstrations
  ├── scripts/                        # Helper scripts and tools
  ├── statistics/                     # Statistical data and logs            
  ├── venv/                           # Python virtual environment
  ├── .env                            # Environment variables
  ├── .gitignore                      
  ├── README.md                       
  ├── render.yaml                     # Render deployment configuration
  └── requirements.txt
```

# 📐 How It Works

Classification & Intent Handling: The system classifies whether the prompt is a direct request or a general question.

Prompt Parsing & Retrieval (RAG): If it is a request, the system breaks it down into sections and queries the SearchService to gather relevant grammar, writing, or reading knowledge from the database.

LLM Generation: The system builds a prompt incorporating the retrieved material and passes it to the LLM (gpt-5-mini or the classification engine) to generate the target HTML structure.

Metadata & Statistics: The backend estimates token usage, measures execution time, and updates the average response time statistics.

# 🛠️ Tech Stack
Layer,Technology
Backend,"Python, FastAPI, Uvicorn"
AI / LLM,"Ollama (API), OpenAI/Open-source models"
Embeddings,sentence-transformers
Vector DB,Qdrant
PDF/HTML export,"fpdf2, HTML generation"

# 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

# 📜 License
All rights reserved.

Krzysztof Sokołowski © 2026

# 👤 Author
KrzysDev — github.com/KrzysDev