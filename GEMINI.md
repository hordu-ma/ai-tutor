# AI Tutor Project Overview

This is a full-stack AI-powered learning management system designed for intelligent homework grading, error analysis, and personalized learning guidance.

## Key Technologies

*   **Backend:** FastAPI (Python 3.12)
*   **Frontend:** Vue.js 3 (TypeScript)
*   **Database:** SQLAlchemy
*   **AI/ML:**
    *   OCR: Tesseract
    *   LLM: OpenAI (GPT), Qwen, Kimi
*   **Package Management:** uv (Python), npm (Node.js)

## Project Structure

*   `src/ai_tutor/`: Backend source code.
    *   `api/`: FastAPI routers and endpoints.
    *   `core/`: Configuration, dependencies, and logging.
    *   `db/`: Database setup and models.
    *   `services/`: Business logic for AI, OCR, and student management.
*   `frontend/`: Frontend source code (Vue.js).
    *   `src/`:
        *   `views/`: Main pages of the application.
        *   `components/`: Reusable UI components.
        *   `router/`: Frontend routing.
        *   `services/`: API communication.
*   `tests/`: Backend tests.
*   `Makefile`: Contains common development commands.
*   `pyproject.toml`: Python dependencies.
*   `package.json`: Frontend dependencies.

## Building and Running

### Backend

1.  **Install dependencies:**
    ```bash
    uv sync
    ```
2.  **Configure environment:**
    Copy `.env.example` to `.env` and fill in the required API keys.
3.  **Run development server:**
    ```bash
    make dev
    ```
    The backend will be available at `http://localhost:8000`.

### Frontend

1.  **Install dependencies:**
    ```bash
    cd frontend
    npm install
    ```
2.  **Run development server:**
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:6173`.

## Development Conventions

*   **Backend Testing:** Run tests with `make test`.
*   **Linting:** Check code quality with `make lint`.
*   **Formatting:** Format code with `make format`.
*   **Git Hooks:** This project uses pre-commit hooks to enforce code style.
*   **Commit Messages:** Follow the conventional commit format (e.g., `feat:`, `fix:`, `docs:`).
