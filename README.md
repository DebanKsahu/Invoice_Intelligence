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
| **🔐 Secure Auth** | OAuth2 integration with **Google** for secure Gmail access (`gmail.readonly`). |
| **📧 Real-time Sync** | **Pub/Sub Webhooks** trigger asynchronous background tasks for non-blocking processing, while persisting `historyId` before job execution to prevent out-of-order event duplication. |
| **🧠 Advanced AI Pipeline** | **Multi-stage processing**: <br>1. **Extraction**: High-fidelity text extraction using **LLMWhisperer**. <br>2. **Validation**: Intelligent document classification to filter non-invoices. <br>3. **Extraction**: Structured data parsing (Vendor, Line Items, Tax) using **Google Gemini**. |
| **📊 Smart Data Export** | Automatically generates comprehensive **Excel** reports with summaries & item breakdowns, and **replies** to the sender with the file attached. |
| **📎 Intelligent Attachment Filtering** | Processes only invoice-like attachments using MIME and extension checks (`pdf`, `png`, `jpg`, `jpeg`, `tiff`, `webp`). |
| **🔁 Loop Prevention** | Skips processing app-generated reply emails by subject match to avoid recursive webhook-triggered processing. |
| **⚡ Async Performance** | Fully asynchronous **SQLAlchemy 2.0** & **SQLModel** ORM with PostgreSQL. |
| **🏗️ Modular Design** | Clean **Domain-Driven Design (DDD)** architecture for maintainability and scale. |
| **🧩 Service Modularization** | Gmail processing is split into focused services (`core_service`, `data_extraction_service`, `mail_service`) for easier maintenance and testing. |
| **⚙️ Robust Config** | Type-safe environment management via **Pydantic Settings**. |
| **🛡️ Middleware** | Production-ready **CORS** and **Session** management. |

## 🛠️ Technology Stack

**Core Infrastructure**
- **Language:** [Python 3.14+](https://www.python.org/)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL (Async via `psycopg` & `SQLModel`)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)

**AI & Processing**
- **LLM/AI:** [LangChain](https://www.langchain.com/), [Google Gemini](https://deepmind.google/technologies/gemini/), [LLMWhisperer](https://unstract.com/llmwhisperer/)
- **Data Manipulation:** `polars` (fast DataFrames) and `xlsxwriter` (Excel reporting).
- **PDF/Image:** `pymupdf` (FitZ), `pdf2image` for robust document handling.

**Integrations & Tooling**
- **Auth:** Google OAuth2 (`google-auth`)
- **Validation:** Pydantic, Msgspec
- **Utilities:** `uuid7` (Time-sorted UIDs)

## 📂 Project Structure

The project follows a Domain-Driven Design inspired structure:

```
src/
├── core/           # Core application logic, DI container, and utilities
├── internal/       # Internal domain modules (Business Logic)
│   ├── auth/       # Authentication domain (Routes, Services, Models)
│   ├── gmail/      # Gmail integration (Webhooks, background jobs, attachment extraction, mail replies)
│   ├── invoice/    # Invoice processing (PDF extraction, AI analysis)
│   ├── platform/   # Infrastructure & Platform concerns (DB, Config, Google API)
│   └── user/       # User domain logic
├── pkg/            # Shared packages and middlewares
└── server/         # Application entry point (main.py)
```

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

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/auth/gmail/initAuth` | Initiates the Google OAuth2 flow for Gmail access. |
| `GET` | `/auth/gmail/callback` | OAuth2 callback handler to exchange code for tokens. |
| `POST` | `/gmail/webhook` | Receives Pub/Sub push notifications, persists history state, and schedules background processing. |

## 🧭 Gmail Webhook Processing Flow

1. Webhook payload is validated and decoded.
2. User is resolved from DB and stale events are ignored (`incoming historyId <= stored historyId`).
3. Latest `historyId` and observer expiry are persisted immediately.
4. Message processing is dispatched via FastAPI background tasks.
5. Attachments are filtered by MIME/extension and reply-generated messages are excluded.
6. Valid invoices are extracted and consolidated into an Excel report.
7. A reply email is sent with `Invoices.xlsx` attached.

## 🤝 Contributing

Contributions are welcome!

1.  **Fork** the repository.
2.  Create a feature branch: `git checkout -b feature/amazing-feature`
3.  **Commit** your changes: `git commit -m 'Add amazing feature'`
4.  **Push** to the branch: `git push origin feature/amazing-feature`
5.  Open a **Pull Request**.

---

_Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com/) and [Python](https://www.python.org/)._
