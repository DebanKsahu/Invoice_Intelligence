# Invoice Intelligence

Invoice Intelligence is a robust backend service tailored for intelligent invoice processing and management. Built with modern Python application standards, it leverages **FastAPI** for high-performance API delivery and integrates seamlessly with Google services for authentication and data retrieval.

The system features a modular architecture designed for scalability, utilising asynchronous database operations with **PostgreSQL** and Type-safe configuration management.

## 🚀 Usage & Features

- **Google Authentication Integration**: Secure OAuth2 flow for **Gmail Read-Only** access (`https://www.googleapis.com/auth/gmail.readonly`), enabling automated invoice retrieval from emails.
- **Gmail Webhook & Pub/Sub Integration**: Real-time notifications for new emails via Google Cloud Pub/Sub webhooks, ensuring immediate processing of invoices.
- **Asynchronous Database**: High-performance async ORM using SQLAlchemy and SQLModel with PostgreSQL.
- **Automatic Schema Management**: Database tables are automatically initialized on startup using SQLModel.
- **Dependency Injection**: Centralized application state and dependency management via `AppDependency`.
- **Structured Logging & Configuration**: Environment-based settings management using Pydantic.
- **Middleware Support**: Integrated CORS and Session middleware for secure and flexible API interactions.

## 🛠 Tech Stack

- **Language**: Python 3.14+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL (Async via `psycopg`, `SQLAlchemy`, & `SQLModel`)
- **Authentication**: Google OAuth2 (`google-auth`, `google-auth-oauthlib`)
- **Validation**: Pydantic & Msgspec
- **Utilities**: `uuid7` for time-sorted unique identifiers

## 📂 Project Structure

The project follows a Domain-Driven Design inspired structure:

```
src/
├── core/           # Core application logic, DI container, and utilities
├── internal/       # Internal domain modules (Business Logic)
│   ├── auth/       # Authentication domain (Routes, Services, Models)
│   ├── gmail/      # Gmail integration (Webhooks, Services, Models)
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

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd Invoice_Intelligence
    ```

2.  **Install Dependencies**
    This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

    ```bash
    uv sync
    ```
    This command will create a virtual environment and install all dependencies as defined in `pyproject.toml`.

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
    ```

### Running the Server
You can run the server using `uv run` to execute commands within the project's environment:

```bash
# Run from the root directory, pointing to the app instance in server/main.py
uv run fastapi dev src/server/main.py
# OR
uv run # OR
uvicorn src.server.main:app --reload
```

The API will be available at `http://localhost:8000`.
Explore the interactive API docs at `http://localhost:8000/docs`.

## 🔌 API Endpoints

### Authentication
- `GET /auth/gmail/initAuth`: Initiates the Google OAuth2 flow.
- `GET /auth/gmail/callback`: Handles the redirect from Google and exchanges code for tokens.

### Gmail
- `POST /gmail/webhook`: Receives push notifications from Google Cloud Pub/Sub containing mailbox updates.
