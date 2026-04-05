# 🧠 AutoTests AI

> AI-powered test generator designed for language teachers

---

## 📖 About

**AITestGenerator** is a tool that allows language teachers to automatically generate language tests using AI. Teachers provide a topic or request, and the system retrieves relevant grammar and vocabulary knowledge using RAG system.

The system is built around an **agentic pipeline**: the AI first creates a plan of action, retrieves relevant content using semantic search, and then generates questions tailored to the student's proficiency level (e.g. B2).

## The problem
My sister and my mom are teachers, and I’ve seen how they prepare tests for their students. It takes a lot of time and is quite boring and repetitive, especially when they need to create multiple versions of the same test to prevent cheating. I realized I could help them by creating a tool that automatically generates such tests. If programmers can vibe-code and then review their code, why can't teachers vibe-create and then review tests?

---

## ✨ Features

- 🤖 AI-generated tests based on teacher prompts (topic, level, number of groups)
- 📚 RAG (Retrieval-Augmented Generation) using Qdrant vector database and sentence-transformers
- 📄 Exports tests to PDF using fpdf2
- 🌐 REST API built with FastAPI
- 🖥️ Frontend interface for test generation and preview
- 🧩 Modular architecture: `backend/`, `frontend/`, `frontend_mock/`, `scripts/`

---

## 🗂️ Project Structure

```
AITestGenerator/
├── backend/          # FastAPI server, RAG pipeline, LLM integration
├── frontend/         # Main frontend application
├── frontend_mock/    # Mock frontend for development/testing
├── scripts/          # Utility scripts (e.g. database seeding)
├── prompt.txt        # Example system prompt used for test generation
├── output.txt        # Example LLM output
├── answer.txt        # Example answer key
├── test.pdf          # Example generated PDF test
├── requirements.txt  # Python dependencies
└── .gitignore
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| AI / LLM | Ollama (local LLM) |
| Embeddings | sentence-transformers, HuggingFace |
| Vector DB | Qdrant |
| PDF export | fpdf2 |
| Data validation | Pydantic v2 |
| HTTP client | httpx, requests |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- [Qdrant](https://qdrant.tech/) instance (local or cloud)

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

3. **Configure environment variables**

Create a `.env` file in the `backend/` directory:

```env
QDRANT_URL=http://localhost:6333
OLLAMA_URL=http://localhost:11434
# Add other config as needed
```

4. **Seed the vector database** (optional, for first-time setup)

```bash
python scripts/<seed_script>.py
```

5. **Start the backend**

```bash
cd backend
uvicorn main:app --reload
```

6. **Start the frontend**

Follow instructions inside the `frontend/` directory.

---

## 📐 How It Works

1. The **teacher** submits a request via the UI (e.g. *"Generate a grammar test on past tenses for B2 students"*).
2. The **backend** uses sentence-transformers to embed the query and retrieves relevant grammar rules from the **Qdrant** vector database (RAG).
3. The retrieved chunks and teacher's request are passed to the **local LLM** (Ollama) with a structured prompt.
4. The LLM generates a test in a defined **JSON schema**:
   - Groups of questions
   - Each question has: `text`, `type` (`multiple_choice` / `open_ended`), `correct_answer`
5. The test can be **exported to PDF** and distributed to students.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## 📜 License

This project does not currently specify a license. Please contact the author for usage permissions.

---

## 👤 Author

**KrzysDev** — [github.com/KrzysDev](https://github.com/KrzysDev)
