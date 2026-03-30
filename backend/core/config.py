import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
WHISPER_MODEL = "whisper-1"
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"

# Determine upload and database directory based on environment
# Use /tmp on Vercel (read-only filesystem), or local directory
if os.environ.get("VERCEL") == "1":
    UPLOAD_DIR = "/tmp/uploads"
    # Use /tmp for SQLite on Vercel (ephemeral)
    DATABASE_URL = "sqlite+aiosqlite:////tmp/pain_mapper.db"
else:
    UPLOAD_DIR = "uploads"
    DATABASE_URL = "sqlite+aiosqlite:///./pain_mapper.db"

# Try to create uploads directory, handle read-only filesystem gracefully
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except (OSError, PermissionError):
    # If we can't create it (read-only filesystem), that's ok for now
    pass
