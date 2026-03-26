# 🧾 Invoice Intelligence

> **Intelligent Invoice Processing & Management Backend**

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-336791.svg)

---

**Invoice Intelligence** is a high-performance, asynchronous backend service designed to automate invoice retrieval and processing. Built with **FastAPI** and **modern Python**, it integrates seamlessly with the **Google Gmail API** for retrieval and leverages **AI (LLMWhisperer & Gemini)** for intelligent data extraction.

This system is engineered for scalability, featuring a modular **Domain-Driven Design (DDD)** architecture, type-safe configuration, and robust PostgreSQL integration.

## 🚀 Features

| Feature | Description |
| :--- | :--- |
| Secure Auth | Google OAuth2 with Gmail read-only scope (`gmail.readonly`). |
| Real-time Sync | Pub/Sub webhook intake with non-blocking `asyncio.create_task` processing. |
| AI Extraction Pipeline | LLMWhisperer extraction, invoice validation, and Gemini-based structured parsing. |
| Excel Output | Generates summary + item-detail worksheets and emails `Invoices.xlsx` to users. |
| Attachment Filtering | Accepts invoice-like files by MIME/extension (`pdf`, `png`, `jpg`, `jpeg`, `tiff`, `webp`). |
| Loop Prevention | Skips app-generated reply emails to prevent recursive processing. |
| Async Stack | Async FastAPI, SQLAlchemy 2.0, and SQLModel with PostgreSQL. |
| Modular Services | Gmail logic split into `core_service`, `data_extraction_service`, and `mail_service`. |
| Typed Config | Pydantic Settings for validated, environment-driven configuration. |
| Structured Logging | Centralized console logging with consistent timestamped format. |
| Middleware | CORS and session middleware enabled for API workflows. |

## 🛠️ Technology Stack

| Category | Stack |
| :--- | :--- |
| Core Infrastructure | [Python 3.14+](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), PostgreSQL (Async via `psycopg` and `SQLModel`), [uv](https://github.com/astral-sh/uv) |
| AI and Processing | [LangChain](https://www.langchain.com/), [Google Gemini](https://deepmind.google/technologies/gemini/), [LLMWhisperer](https://unstract.com/llmwhisperer/), `pymupdf`, `pdf2image`, `polars`, `xlsxwriter` |
| Integrations and Tooling | Google OAuth2 (`google-auth`), Pydantic, Msgspec, Python `logging` via `core/LoggingConfig.py`, `uuid7` |

## ⚡ Getting Started

### Prerequisites

- Python 3.14 or higher
- PostgreSQL Database
- Google Cloud Console Project (for OAuth credentials)

### 📥 Installation

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd Invoice_Intelligence
    ```

2.  **Install Dependencies**
    Initialize the environment and sync dependencies using `uv`:
    ```bash
    uv sync
    ```
    > This creates a virtual environment and installs all packages defined in `pyproject.toml`.

3.  **Environment Configuration**
    Create a `.env` file in the root directory (based on `src/internal/platform/config/Settings.py`). The configuration uses nested delimiters (`.`).

    ```ini
    # Database Settings
    database_settings.DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/invoice_db

    # Google Settings
    google_settings.CLIENT_ID=your_google_client_id
    google_settings.CLIENT_SECRET=your_google_client_secret
    google_settings.AUTH_URI=https://accounts.google.com/o/oauth2/auth
    google_settings.TOKEN_URI=https://oauth2.googleapis.com/token
    google_settings.AUTH_CALLBACK_URL=http://localhost:8000/auth/gmail/callback
    google_settings.GMAIL_PUBSUB_TOPIC_NAME=projects/your-project/topics/gmail-updates
    google_settings.GMAIL_PUBSUB_CALLBACK_URL=https://your-domain.com/gmail/webhook

    # AI & LLM Settings
    llmwhisperer_settings.API_KEY=your_llm_whisperer_api_key
    llmwhisperer_settings.BASE_URL=https://llmwhisperer-api.unstract.com/v2
    google_gemini_settings.API_KEY=your_google_gemini_api_key
    ```

### ▶️ Running the Server

Run the application within the project's environment:

```bash
# Development Mode (Hot Reload)
uv run fastapi dev src/server/main.py

# Production Mode
uv run uvicorn src.server.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
Explore the interactive API docs at `http://localhost:8000/docs`.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| GET | `/auth/gmail/initAuth` | Starts Google OAuth2 flow for Gmail access. |
| GET | `/auth/gmail/callback` | Handles OAuth2 callback and token exchange. |
| POST | `/gmail/webhook` | Handles Pub/Sub events, persists state, and schedules async processing. |

## 🧭 Gmail Webhook Processing Flow

1. Validate and decode webhook payload.
2. Resolve user and ignore stale events (`incoming historyId <= stored historyId`).
3. Persist latest `historyId` and observer expiry.
4. Dispatch async processing via `asyncio.create_task`.
5. Filter attachments and exclude reply-generated messages.
6. Extract invoice data and build Excel sheets (`Invoice Summary`, `Invoice Item Detail`).
7. Send reply email with `Invoices.xlsx`.

## 🤝 Contributing

Contributions are welcome!

1.  **Fork** the repository.
2.  Create a feature branch: `git checkout -b feature/amazing-feature`
3.  **Commit** your changes: `git commit -m 'Add amazing feature'`
4.  **Push** to the branch: `git push origin feature/amazing-feature`
5.  Open a **Pull Request**.

---

_Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com/) and [Python](https://www.python.org/)._
