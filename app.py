"""واجهة API + واجهة الطالب + لوحة الإدارة.
التشغيل: uvicorn app:app --reload   ثم افتح http://localhost:8000   (ولوحة الإدارة: /admin)"""
import re
import threading

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import config
from rag import analytics
from rag.index import Index
from rag.loaders import SUPPORTED
from rag.pipeline import ask

app = FastAPI(title="المرشد الأكاديمي الذكي")
_lock = threading.Lock()
state = {"index": None}


def get_index() -> Index:
    if state["index"] is None:
        with _lock:
            if state["index"] is None:
                try:
                    state["index"] = Index.load()
                except FileNotFoundError:
                    state["index"] = Index.build()
    return state["index"]


class Message(BaseModel):
    role: str
    content: str = Field(max_length=4000)


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    history: list[Message] = []
    source: str | None = None   # تصفية اختيارية بمستند واحد


@app.get("/")
def home():
    return FileResponse(config.ROOT / "static" / "index.html")


@app.get("/admin")
def admin_page():
    return FileResponse(config.ROOT / "static" / "admin.html")


def _require_admin(token: str):
    if not config.ADMIN_TOKEN or token != config.ADMIN_TOKEN:
        raise HTTPException(401, "رمز المشرف غير صحيح.")


@app.get("/api/health")
def health():
    idx = get_index()
    titles = {}
    for c in idx.chunks:
        titles.setdefault(c.source, c.meta.get("doc") or c.source)
    return {"status": "ok", "chunks": len(idx.chunks),
            "documents": [{"source": s, "title": t} for s, t in sorted(titles.items())]}


@app.post("/api/ask")
def api_ask(req: AskRequest):
    try:
        answer = ask(get_index(), req.question, [m.model_dump() for m in req.history], req.source)
    except Exception as e:  # لا نكشف تفاصيل داخلية للمستخدم
        print("ERROR:", repr(e))
        raise HTTPException(502, "تعذّر توليد الإجابة الآن. حاول مرة أخرى.")
    analytics.log(answer)
    return answer.to_dict()


@app.get("/api/stats")
def api_stats(x_admin_token: str = Header(default="")):
    _require_admin(x_admin_token)
    return analytics.stats()


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), x_admin_token: str = Header(default="")):
    _require_admin(x_admin_token)
    name = re.sub(r"[^\w.\-]", "_", file.filename or "")  # منع مسارات خبيثة مثل ../../
    if not name or not any(name.lower().endswith(ext) for ext in SUPPORTED):
        raise HTTPException(400, f"الصيغ المدعومة: {', '.join(sorted(SUPPORTED))}")
    data = await file.read()
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"الحد الأقصى {config.MAX_UPLOAD_MB} ميغابايت.")
    (config.DOCS_DIR / name).write_bytes(data)
    with _lock:
        state["index"] = Index.build()
    return {"uploaded": name, "chunks": len(state["index"].chunks)}
