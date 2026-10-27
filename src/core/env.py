import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SRC_DIR = Path(__file__).resolve().parent.parent  # ../src
INSTRUCTIONS_DIR = SRC_DIR / "agents" / "instructions"
DOCS_DIR = SRC_DIR / "docs"
OUPUT_DIR = SRC_DIR / "output"


def _required_env(name: str) -> str:
    """Memeriksa apakah environment variable wajib sudah diatur."""

    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' belum di-set"
        )

    return value


GEMINI_API_KEY = _required_env("GEMINI_API_KEY")
GEMINI_MODEL = _required_env("GEMINI_MODEL")
GEMINI_MODEL_TTS = _required_env("GEMINI_MODEL_TTS")

SUPABASE_URL = _required_env("SUPABASE_URL")
SUPABASE_KEY = _required_env("SUPABASE_KEY")

TELEGRAM_BOT_TOKEN = _required_env("TELEGRAM_BOT_TOKEN")
FASTAPI_PUBLIC_URL = os.getenv("FASTAPI_PUBLIC_URL", "").rstrip("/")

TELEGRAM_WEBHOOK_URL = (
    os.getenv("TELEGRAM_WEBHOOK_URL")
    or (
        f"{FASTAPI_PUBLIC_URL}/webhook"
        if FASTAPI_PUBLIC_URL
        else ""
    )
)
TELEGRAM_SECRET_TOKEN = _required_env("TELEGRAM_SECRET_TOKEN")
