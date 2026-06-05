import sqlite3
import time
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import run_pipeline

app = FastAPI(title="AI Compiler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
    max_age=3600,
)


def init_db():
    conn = sqlite3.connect("metrics.db")
    # Create with full 9-column schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            job_id            TEXT PRIMARY KEY,
            prompt            TEXT,
            status            TEXT,
            provider          TEXT,
            latency_seconds   REAL,
            total_tokens      INTEGER,
            repair_attempts   INTEGER,
            validation_errors INTEGER,
            created_at        REAL
        )
    """)
    # Safe migration: add provider column if old 8-column schema exists
    try:
        conn.execute("ALTER TABLE runs ADD COLUMN provider TEXT DEFAULT 'groq'")
    except Exception:
        pass  # column already exists — ignore
    conn.commit()
    conn.close()

init_db()


def save_metrics(job_id: str, prompt: str, result: dict):
    conn = sqlite3.connect("metrics.db")
    m = result.get("metrics", {})
    conn.execute(
        """INSERT OR REPLACE INTO runs
           (job_id, prompt, status, provider, latency_seconds, total_tokens,
            repair_attempts, validation_errors, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            job_id,
            prompt[:500],
            result.get("status"),
            "groq",
            m.get("total_latency_seconds", 0),
            m.get("total_tokens", 0),
            m.get("repair_attempts", 0),
            len(result.get("validation_errors", [])),
            time.time(),
        ),
    )
    conn.commit()
    conn.close()


class GenerateRequest(BaseModel):
    prompt: str


@app.post("/generate")
async def generate(req: GenerateRequest):
    if not req.prompt or len(req.prompt.strip()) < 10:
        raise HTTPException(status_code=400, detail="Prompt too short.")
    try:
        result = run_pipeline(req.prompt.strip())
        save_metrics(result["job_id"], req.prompt, result)
        return result
    except Exception as e:
        print("PIPELINE ERROR:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def get_metrics():
    conn = sqlite3.connect("metrics.db")
    rows = conn.execute(
        "SELECT job_id, prompt, status, provider, latency_seconds, total_tokens, "
        "repair_attempts, validation_errors, created_at FROM runs ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    cols  = ["job_id", "prompt", "status", "provider", "latency_seconds",
             "total_tokens", "repair_attempts", "validation_errors", "created_at"]
    data    = [dict(zip(cols, row)) for row in rows]
    total   = len(data)
    success = sum(1 for r in data if r["status"] == "success")
    return {
        "total_runs":    total,
        "success_rate":  round(success / total * 100, 1) if total else 0,
        "avg_latency":   round(sum(r["latency_seconds"] for r in data) / total, 2) if total else 0,
        "total_repairs": sum(r["repair_attempts"] for r in data),
        "runs": data,
    }


@app.get("/health")
def health():
    return {"status": "ok", "provider": "groq", "model": "llama-3.3-70b-versatile"}
