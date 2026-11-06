"""كل الإعدادات من متغيرات البيئة (ملف .env). لا مفاتيح داخل الكود."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).parent


def _env(name, default):
    return os.getenv(name, default)


# البيانات
DOCS_DIR = ROOT / _env("DOCS_DIR", "data/docs")
INDEX_DIR = ROOT / _env("INDEX_DIR", "data/index")
PDF_RTL_FIX = _env("PDF_RTL_FIX", "auto")          # auto | on | off

# التقطيع
CHUNK_SIZE = int(_env("CHUNK_SIZE", "700"))         # بالأحرف (~130-150 كلمة عربية)؛ مواد اللائحة قصيرة
CHUNK_OVERLAP = int(_env("CHUNK_OVERLAP", "150"))

# الاسترجاع
EMBEDDING_BACKEND = _env("EMBEDDING_BACKEND", "local")   # local | openai
EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
TOP_K = int(_env("TOP_K", "5"))
CANDIDATES = int(_env("CANDIDATES", "20"))          # عدد المرشحين قبل الدمج/إعادة الترتيب
HYBRID_ALPHA = float(_env("HYBRID_ALPHA", "0.5"))   # وزن البحث الدلالي مقابل BM25
RERANK = _env("RERANK", "false").lower() == "true"
RERANK_MODEL = _env("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
MIN_SIMILARITY = float(_env("MIN_SIMILARITY", "0"))  # 0 = معطّل. عايِره بعد تشغيل evaluate.py

# النموذج اللغوي
LLM_PROVIDER = _env("LLM_PROVIDER", "anthropic")    # anthropic | openai (أو أي خدمة متوافقة)
LLM_MODEL = _env("LLM_MODEL", "claude-haiku-5-5")
LLM_BASE_URL = _env("LLM_BASE_URL", "") or None     # مثلًا Groq أو Ollama أو OpenRouter
LLM_TEMPERATURE = float(_env("LLM_TEMPERATURE", "0"))
MAX_TOKENS = int(_env("MAX_TOKENS", "800"))
REWRITE_QUERIES = _env("REWRITE_QUERIES", "true").lower() == "true"

# التكلفة (دولار لكل مليون token) — عبّئها من صفحة أسعار المزوّد
PRICE_INPUT_PER_MTOK = float(_env("PRICE_INPUT_PER_MTOK", "0"))
PRICE_OUTPUT_PER_MTOK = float(_env("PRICE_OUTPUT_PER_MTOK", "0"))

# الأمان
ADMIN_TOKEN = _env("ADMIN_TOKEN", "")               # مطلوب لرفع المستندات عبر الواجهة
MAX_UPLOAD_MB = int(_env("MAX_UPLOAD_MB", "20"))
LOG_QUESTIONS = _env("LOG_QUESTIONS", "true").lower() == "true"  # سجل الأسئلة للوحة الإحصاءات

REFUSAL = "لا تتوفر لديّ معلومات كافية في المستندات المتاحة للإجابة عن هذا السؤال."
