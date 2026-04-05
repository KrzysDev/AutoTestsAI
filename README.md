# 🧠 AutoTests AI

> AI-powered test generator designed for language teachers

---

## 📖 About

**AutoTests AI** is a tool that allows language teachers to automatically generate language tests using AI. Teachers provide a topic or request, and the system retrieves relevant grammar and vocabulary knowledge using RAG system.

The system is built around an **agentic pipeline**: the AI first creates a plan of action, retrieves relevant content using semantic search, and then generates questions tailored to the student's proficiency level (e.g. B2).

## The problem
My sister and my mom are teachers, and I’ve seen how they prepare tests for their students. It takes a lot of time and is quite boring and repetitive, especially when they need to create multiple versions of the same test to prevent cheating. I realized I could help them by creating a tool that automatically generates such tests. If programmers can vibe-code and then review their code, why can't teachers vibe-create and then review tests?

---

## ✨ Features

- 🤖 AI-generated tests based on teacher prompts (topic, level, number of groups)
- 📚 RAG (Retrieval-Augmented Generation) using Qdrant vector database and sentence-transformers
- 📄 Exports tests to PDF using fpdf2
- 🌐 REST API built with FastAPI
- 🖥️ Mock-Frontend cli interface

---

## 🗂️ Project Structure

```
TestGenerator/
├── backend/                # Backend (FastAPI)
│   └── app/
│       ├── api/            # API endpoints and controllers
│       ├── core/           # Configuration, settings, security
│       ├── models/         # Data models (SQLAlchemy/Pydantic)
│       ├── services/       # Business logic of the project
│       └── main.py         # Entry point of the backend application
├── frontend/               # Frontend 
│   ├── main_app.py         # Main file of the frontend application
│   └── main_app.spec       # PyInstaller configuration (to build execa)
├── frontend_mock/          # Mock/CLI version of the frontend (according to the project history)
├── scripts/                # Helper scripts
│   ├── tests/              # Tests for scripts
│   └── tools/              # Utility tools
├── venv/                   # Python virtual environment
├── .gitignore              # Files ignored by Git
├── README.md               # Project documentation
└── requirements.txt        # List of Python dependencies

```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| AI / LLM | Ollama (API) |
| Embeddings | sentence-transformers |
| Vector DB | Qdrant |
| PDF export | fpdf2 |

---

## 🚀 Want to try out the app?



## 🔍 How to see whats inside...

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/KrzysDev/AITestGenerator.git
cd AITestGenerator
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```
3. **Start the backend**

```bash
# from root directory
uvicorn backend.app.main:app --reload
```

4. **Start the frontend**

```bash
# from root directory
python frontend/main_app.py
```

## 📐 How It Works

1. The **teacher** submits a request via the UI (e.g. *"Generate a grammar test on past tenses for B2 students"*).
2. The **backend** uses sentence-transformers to embed the query and retrieves relevant grammar rules from the **Qdrant** vector database (RAG).
3. The retrieved chunks and teacher's request are passed to the **LLM** (Ollama) with a structured prompt.
4. The LLM generates a test in a defined **JSON schema**:
   - Groups of questions
   - Each question has: `text`, `type` (`multiple_choice` / `open_ended`), `correct_answer`
5. Then the system converts json into .pdf file.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## 📜 License

All rights reserved.

Krzysztof Sokołowski © 2026

---

## 👤 Author

**KrzysDev** — [github.com/KrzysDev](https://github.com/KrzysDev)
