import os


class Config:
    """
    Base configuration for the Flask application.

    This centralizes environment-driven settings so the rest of the
    codebase can import a single source of truth.
    """

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai-receptionist-secret-key-change-in-prod")

    # Database settings – stored inside backend/database/
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database", "app.db")

    # Groq API settings
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


config = Config()

