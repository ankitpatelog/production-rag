import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_COLLECTION = "enterprise_rag"
    
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    GROK_FALLBACK_API_KEY = os.getenv("GROK_FALLBACK_API_KEY")
    GROK_MODEL = "llama-3.3-70b-versatile"
    
settings = Settings()
