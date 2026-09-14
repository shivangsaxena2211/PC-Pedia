import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "pc_pedia.db")


def _sqlite_uri(db_path: str) -> str:
    """Build a SQLAlchemy-compatible SQLite URI (handles Windows paths)."""
    return "sqlite:///" + db_path.replace("\\", "/")


def _resolve_database_uri() -> str:
    """
    Return the canonical SQLite database URI for PC Pedia.

    SQLite is the default and only supported database for this project.
    DATABASE_URL may override the path when it is a sqlite:// URI.
    Non-SQLite DATABASE_URL values are ignored.
    """
    default = _sqlite_uri(DEFAULT_DB_PATH)
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return default
    if url.startswith("sqlite:"):
        return url
    return default


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
    }
    ITEMS_PER_PAGE = 24
    MAX_ITEMS_PER_PAGE = 100
