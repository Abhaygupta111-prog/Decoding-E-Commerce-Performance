"""
Reusable SQLAlchemy connection to the Cart2Insights database.
Supports both SQLite (DB_ENGINE=sqlite, default — no server needed, great for
local dev/grading) and MySQL (DB_ENGINE=mysql, for production-style setups).
Credentials are read from environment variables (.env) — never hardcoded.

Usage:
    from database import get_engine
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM orders LIMIT 5", engine)
"""

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Project root = one level up from this file (streamlit/database.py -> project/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_engine():
    """Create and return a SQLAlchemy engine, backend chosen by DB_ENGINE env var."""
    db_engine = os.getenv("DB_ENGINE", "sqlite").lower()

    if db_engine == "sqlite":
        db_path = os.getenv("SQLITE_PATH", "data/cart2insights.db")
        if not os.path.isabs(db_path):
            db_path = os.path.join(PROJECT_ROOT, db_path)
        conn_str = f"sqlite:///{db_path}"
        return create_engine(conn_str)

    elif db_engine == "mysql":
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME")

        missing = [k for k, v in {
            "DB_USER": user, "DB_PASSWORD": password, "DB_NAME": db_name
        }.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Copy .env.example to .env and fill in your credentials."
            )

        conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        return create_engine(conn_str)

    else:
        raise ValueError(f"Unknown DB_ENGINE '{db_engine}'. Use 'sqlite' or 'mysql'.")


def test_connection():
    """Quick sanity check that the DB connection works."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT 1")
        print("Connection OK:", result.fetchone())


if __name__ == "__main__":
    test_connection()
