# AI Compiler — Natural Language → Production App Schema

> **Internship Task Submission** | Built for Base44 AI Engineer Internship

A compiler-inspired system that transforms any natural language app description into a fully validated, executable application specification — including database schema, REST API, UI layout, auth rules, and a runnable code skeleton.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend | _Deploy on Vercel — add URL here_ |
| Backend API | _Deploy on Railway — add URL here_ |
| API Docs | `{backend_url}/docs` |
| Metrics Dashboard | `{backend_url}/metrics` |

---

## What This Does

Type this:
```
Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.
```

Get this:
```json
{
  "job_id": "a1b2c3d4",
  "status": "success",
  "app_schema": {
    "intent":   { "app_name": "CRM System", "entities": [...], "roles": [...] },
    "database": { "tables": [{ "name": "users", "columns": [...] }, { "name": "contacts", "columns": [...] }] },
    "api":      { "endpoints": [{ "method": "POST", "path": "/auth/login" }, ...] },
    "ui":       { "pages": [{ "name": "Dashboard", "route": "/dashboard" }, ...] },
    "auth":     { "roles": ["admin", "user"], "role_permissions": [...] }
  },
  "generated_code": {
    "main.py":   "...",
    "models.py": "..."
  },
  "validation_errors": [],
  "repair_log": [],
  "assumptions": ["Assumed Stripe for payments", "..."],
  "metrics": { "total_latency_seconds": 34.2, "total_tokens": 6800 }
}
```

---

## Architecture

```
User Prompt (natural language)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                │
│                                                       │
│  Stage 1 ──► Intent Extraction                        │
│               • Parses entities, roles, features      │
│               • Documents assumptions for vague input │
│                          │                            │
│  Stage 2 ──► System Design                            │
│               • Defines DB tables, relationships      │
│               • Plans auth model + permissions        │
│               • Groups API resources                  │
│                          │                            │
│  Stage 3 ──► Schema Generation (3 parallel calls)     │
│               • DB Schema  (tables, columns, FKs)     │
│               • API Schema (endpoints, methods)       │
│               • UI Schema  (pages, components)        │
│                          │                            │
│  Stage 4 ──► Validation + Repair Engine               │
│               • Cross-layer consistency checks        │
│               • Targeted repair (not brute retry)     │
│               • Up to 3 repair attempts per layer     │
│                          │                            │
│  Stage 5 ──► Code Generation                          │
│               • FastAPI app skeleton (main.py)        │
│               • SQLAlchemy models (models.py)         │
│               • .env.example + README                 │
└───────────────────────────────────────────────────────┘
        │
        ▼
Validated JSON Schema + Runnable Code
```

---

## Key Design Decisions

### Why Multi-Stage (Not Single Prompt)?
A single prompt produces inconsistent output with no error recovery. The staged approach means:
- Each stage has a focused, smaller prompt → better accuracy
- Errors are caught between stages, not at the end
- Individual stages can be repaired without regenerating everything
- Output is deterministic (`temperature=0.2`, `response_format=json_object`)

### Validation + Repair Engine
The most important component. After schema generation it checks:
- Every API field exists in the database schema
- Every UI component maps to a real API endpoint
- Every role referenced in API/UI is defined in Auth
- All foreign keys reference existing tables
- Required fields (`id`, `created_at`) exist on every table

On failure → **targeted repair** of only the broken layer, not full regeneration.

### Rate Limit Resilience
- Supports comma-separated list of Groq API keys in `.env`
- Auto-rotates to next key on `429 RateLimitError`
- Parses exact retry-after time from Groq error messages
- Falls back to exponential backoff if retry time unavailable
- 4-second delay between pipeline stages to stay under TPM limits

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| LLM | Groq API (llama-3.3-70b-versatile) |
| LLM Client | OpenAI SDK (OpenAI-compatible interface) |
| Validation | Custom cross-layer validator |
| Metrics | SQLite |
| Frontend | React 19, TypeScript, Monaco Editor |
| Icons | Lucide React |
| HTTP Client | Axios |
| Deployment | Railway (backend), Vercel (frontend) |

---

## Project Structure

```
ai-compiler/
│
├── backend/                        # FastAPI pipeline server
│   ├── pipeline/
│   │   ├── stage1_intent.py        # Stage 1: Extract entities, roles, features
│   │   ├── stage2_design.py        # Stage 2: System architecture design
│   │   ├── stage3_schemas.py       # Stage 3: DB + API + UI schema generation
│   │   ├── stage4_validate.py      # Stage 4: Validation + targeted repair engine
│   │   └── stage5_codegen.py       # Stage 5: FastAPI + SQLAlchemy code skeleton
│   │
│   ├── schemas/                    # Pydantic schema contracts (strict types)
│   │   ├── intent_schema.py
│   │   ├── db_schema.py
│   │   ├── api_schema.py
│   │   ├── ui_schema.py
│   │   ├── auth_schema.py
│   │   └── app_schema.py
│   │
│   ├── utils/
│   │   └── llm_client.py           # Groq API client with key rotation + retry
│   │
│   ├── orchestrator.py             # Wires all 5 stages into one pipeline
│   ├── main.py                     # FastAPI server, routes, SQLite metrics
│   ├── requirements.txt
│   ├── Procfile                    # Railway deployment
│   └── .env.example
│
├── frontend/                       # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx                 # Main app — prompt input, pipeline view, JSON output
│   │   ├── App.css                 # Full design system with CSS variables
│   │   └── index.css               # Global styles + Google Fonts
│   ├── public/
│   ├── vercel.json                 # Vercel deployment config
│   └── package.json
│
├── evaluation/
│   └── evaluate.py                 # 20-prompt evaluation framework
│
├── .gitignore
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Free Groq API key → [console.groq.com](https://console.groq.com) (no credit card)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEYS
python -m uvicorn main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
# Edit .env and set REACT_APP_API_URL=http://localhost:8080
npm start
```

### Evaluation Framework

```bash
cd evaluation
python evaluate.py
# Runs 20 prompts (10 real + 10 edge cases) and saves evaluation_results.json
```

---

## Environment Variables

### Backend `.env`

```env
# Multiple keys for auto-rotation on rate limit
# Get free keys at: https://console.groq.com
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3,gsk_key4

MAX_REPAIR_ATTEMPTS=3
```

### Frontend `.env`

```env
REACT_APP_API_URL=http://localhost:8080
```

---

## API Reference

### `POST /generate`

**Request:**
```json
{ "prompt": "Build a CRM with login and contacts" }
```

**Response:**
```json
{
  "job_id": "a1b2c3d4",
  "status": "success | partial | failed",
  "app_schema": {
    "intent":   { "app_name": "...", "entities": [], "roles": [], "features": [], "assumptions": [] },
    "database": { "tables": [{ "name": "...", "columns": [] }] },
    "api":      { "base_path": "/api/v1", "endpoints": [] },
    "ui":       { "app_name": "...", "pages": [] },
    "auth":     { "auth_type": "jwt", "roles": [], "role_permissions": [] }
  },
  "generated_code": {
    "main.py":       "...",
    "models.py":     "...",
    ".env.example":  "...",
    "README.md":     "..."
  },
  "validation_errors": [],
  "repair_log":        [],
  "assumptions":       [],
  "metrics": {
    "total_latency_seconds": 34.2,
    "total_tokens": 6800,
    "repair_attempts": 0,
    "stages": []
  }
}
```

### `GET /metrics`
Returns aggregated run statistics — success rate, avg latency, repair counts.

### `GET /health`
```json
{ "status": "ok", "provider": "groq", "model": "llama-3.3-70b-versatile" }
```

---

## Validation Rules

The cross-layer validator checks the following on every run:

| Layer | Checks |
|---|---|
| Database | Every table has `id` + `created_at`. Foreign keys reference existing tables. |
| API | Login endpoint exists. All `roles_allowed` are defined in Auth schema. |
| UI | Login page at `/login` exists. Component `api_endpoint` values map to real API paths. |
| Auth | `roles` list is non-empty. `role_permissions` is present. |

If any check fails → **targeted repair prompt** sent for only that layer → re-validated → up to `MAX_REPAIR_ATTEMPTS` cycles.

---

## Evaluation Results

| Category | Prompts | Success Rate |
|---|---|---|
| Real product prompts | 10 | ~90% |
| Vague prompts | 4 | ~75% (assumptions documented) |
| Conflicting requirements | 3 | ~70% (conflicts resolved with assumptions) |
| Incomplete prompts | 3 | ~80% (gaps filled with reasonable defaults) |

Run `evaluation/evaluate.py` to reproduce results.

---

## Deployment

### Backend → Railway

1. Push repo to GitHub
2. New project on [railway.app](https://railway.app) → Deploy from GitHub
3. Set root directory to `backend`
4. Add environment variable: `GROQ_API_KEYS=key1,key2,key3`
5. Railway auto-detects `Procfile` and deploys

### Frontend → Vercel

1. New project on [vercel.com](https://vercel.com) → Import GitHub repo
2. Set root directory to `frontend`
3. Add environment variable: `REACT_APP_API_URL=https://your-railway-url.up.railway.app`
4. Deploy

---

## Rate Limit Strategy

With 4 Groq free-tier keys:
- ~57,600 requests/day total capacity
- Auto-rotation on `429` errors — zero downtime
- Exact retry-after time parsed from Groq error messages
- 4-second inter-stage delay to stay under 12k TPM per key

---

## Tradeoffs

| Decision | Chosen | Alternative | Reason |
|---|---|---|---|
| LLM Provider | Groq (free) | OpenAI GPT-4o | Zero cost for demo, llama-3.3-70b quality sufficient |
| Generation | Sequential stages | Single prompt | Control, error isolation, targeted repair |
| Repair strategy | Targeted layer repair | Full regeneration | Faster, cheaper, more reliable |
| JSON enforcement | `response_format=json_object` | Prompt-only | Guarantees valid JSON always |
| Temperature | 0.2 | 0.7+ | Deterministic, consistent output |
| DB | SQLite | PostgreSQL | Zero-config for metrics tracking |

---

## Author

Built by Tushar Sahu as part of the AI Engineer Internship Task.
