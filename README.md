<div align="center">

# 🧠 AI Compiler — Natural Language → Production App Schema

**Internship Task Submission · Base44 AI Engineer Internship · Tushar Sahu**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-orange)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

A compiler-inspired, 5-stage LLM pipeline that transforms any plain-English app description into a fully validated, production-ready application specification — complete with database schema, REST API design, UI layout, auth rules, and a runnable FastAPI + SQLAlchemy code skeleton.

</div>

---

## 📺 Live Demo

| Service | URL |
|---|---|
| Frontend | _Deploy on Vercel — add URL here_ |
| Backend API | _Deploy on Railway — add URL here_ |
| API Docs (Swagger) | `{backend_url}/docs` |
| Metrics Dashboard | `{backend_url}/metrics` |
| Health Check | `{backend_url}/health` |

---

## ⚡ What It Does — In 10 Seconds

**Input** — plain English:
```
Build a CRM with login, contacts, dashboard, role-based access,
and premium plan with payments. Admins can see analytics.
```

**Output** — ~35 seconds later, a fully validated JSON spec + runnable code:

```json
{
  "job_id": "a1b2c3d4",
  "status": "success",
  "app_schema": {
    "intent": {
      "app_name": "CRM System",
      "app_type": "CRM",
      "entities": [
        { "name": "User",    "attributes": ["id", "email", "role", "password_hash"] },
        { "name": "Contact", "attributes": ["id", "name", "email", "owner_id"] }
      ],
      "roles": [
        { "name": "admin", "permissions": ["contacts:read", "contacts:write", "analytics:read"] },
        { "name": "user",  "permissions": ["contacts:read", "contacts:write"] }
      ],
      "features": [
        { "name": "Authentication",     "requires_auth": false },
        { "name": "Contact Management", "requires_auth": true  },
        { "name": "Analytics Dashboard","requires_auth": true  }
      ],
      "assumptions": ["Assumed Stripe for payments", "Assumed JWT for auth"]
    },
    "database": {
      "tables": [
        {
          "name": "users",
          "columns": [
            { "name": "id",            "type": "integer", "primary_key": true },
            { "name": "email",         "type": "string",  "unique": true, "nullable": false },
            { "name": "password_hash", "type": "string",  "nullable": false },
            { "name": "role",          "type": "string",  "nullable": false },
            { "name": "created_at",    "type": "datetime" }
          ]
        },
        {
          "name": "contacts",
          "columns": [
            { "name": "id",         "type": "integer", "primary_key": true },
            { "name": "name",       "type": "string",  "nullable": false },
            { "name": "email",      "type": "string" },
            { "name": "owner_id",   "type": "integer", "foreign_key": "users.id" },
            { "name": "created_at", "type": "datetime" }
          ]
        }
      ]
    },
    "api": {
      "base_path": "/api/v1",
      "endpoints": [
        { "method": "POST", "path": "/auth/login",        "auth_required": false },
        { "method": "POST", "path": "/auth/register",     "auth_required": false },
        { "method": "GET",  "path": "/contacts",          "auth_required": true, "roles_allowed": ["admin","user"] },
        { "method": "POST", "path": "/contacts",          "auth_required": true, "roles_allowed": ["admin","user"] },
        { "method": "GET",  "path": "/analytics/summary", "auth_required": true, "roles_allowed": ["admin"] }
      ]
    },
    "ui": {
      "pages": [
        { "name": "Login",     "route": "/login",     "auth_required": false },
        { "name": "Dashboard", "route": "/dashboard", "auth_required": true  },
        { "name": "Contacts",  "route": "/contacts",  "auth_required": true  }
      ]
    },
    "auth": {
      "auth_type": "jwt",
      "roles": ["admin", "user"],
      "role_permissions": [
        { "role": "admin", "permissions": ["contacts:read","contacts:write","analytics:read"] },
        { "role": "user",  "permissions": ["contacts:read","contacts:write"] }
      ]
    }
  },
  "generated_code": {
    "models.py": "from sqlalchemy import Column, Integer, String ...",
    "main.py":   "from fastapi import FastAPI ..."
  },
  "validation_errors": [],
  "repair_log":        [],
  "assumptions":       ["Assumed Stripe for payments", "Assumed JWT auth"],
  "metrics": {
    "total_latency_seconds": 34.2,
    "total_tokens": 6800,
    "estimated_cost_usd": 0.0,
    "repair_attempts": 0
  }
}
```

---

## 🗺️ High-Level Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                        AI COMPILER SYSTEM                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   Browser (React 19 + TypeScript)                                ║
║   ┌─────────────────────────────────────────────────────────┐   ║
║   │  Prompt Input  →  POST /generate  →  Tabbed JSON Output │   ║
║   │  Monaco Editor · Pipeline Progress · Metrics Panel      │   ║
║   └──────────────────────────┬──────────────────────────────┘   ║
║                              │ HTTP / Axios                      ║
║   FastAPI Server (Python 3.12)                                   ║
║   ┌──────────────────────────▼──────────────────────────────┐   ║
║   │  POST /generate  →  orchestrator.run_pipeline()         │   ║
║   │  GET  /metrics   →  SQLite aggregated stats             │   ║
║   │  GET  /health    →  provider + model status             │   ║
║   └──────────────────────────┬──────────────────────────────┘   ║
║                              │                                   ║
║   Pipeline (5 Stages)        │                                   ║
║   ┌──────────────────────────▼──────────────────────────────┐   ║
║   │  Stage 1: Intent Extraction    (1 LLM call)             │   ║
║   │  Stage 2: System Design        (1 LLM call)             │   ║
║   │  Stage 3: Schema Generation    (3 LLM calls)            │   ║
║   │  Stage 4: Validation + Repair  (0–3 LLM calls)          │   ║
║   │  Stage 5: Code Generation      (0 LLM calls, pure Python)│  ║
║   └──────────────────────────┬──────────────────────────────┘   ║
║                              │                                   ║
║   LLM Client                 │                                   ║
║   ┌──────────────────────────▼──────────────────────────────┐   ║
║   │  Groq API (llama-3.3-70b-versatile)                     │   ║
║   │  Key rotation · Retry-after parsing · Backoff           │   ║
║   └─────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🔄 Full Pipeline Data Flow

```
User Prompt (string)
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Intent Extraction                stage1_intent.py      │
│                                                                   │
│  Input:  raw user prompt (string)                                 │
│  LLM:    system prompt enforces IntentSchema structure            │
│  Output: IntentSchema {                                           │
│            app_name, app_type,                                    │
│            entities[{name, attributes[], relationships[]}],       │
│            roles[{name, permissions[]}],                          │
│            features[{name, description, requires_auth}],          │
│            assumptions[], clarifications_needed[]                 │
│          }                                                        │
│  + sleep(4s) rate-limit buffer                                    │
└──────────────────────────┬────────────────────────────────────────┘
                           │ IntentSchema dict
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│  STAGE 2 — System Design                    stage2_design.py      │
│                                                                   │
│  Input:  IntentSchema dict                                        │
│  LLM:    system prompt enforces DesignSchema structure            │
│  Output: DesignSchema {                                           │
│            entities[{name, db_table, fields[{                     │
│              name, type, nullable, unique,                        │
│              primary_key, foreign_key}]}],                        │
│            flows[{name, steps[], roles_involved[]}],              │
│            auth_design{type, roles[], role_permissions[]},        │
│            api_groups[{resource, operations[]}]                   │
│          }                                                        │
│  + sleep(4s) rate-limit buffer                                    │
└──────────────────────────┬────────────────────────────────────────┘
                           │ DesignSchema dict
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Schema Generation               stage3_schemas.py      │
│                                                                   │
│  Builds a compact context from design:                            │
│  { app, entities[], roles[], api_groups[], features[] }           │
│                                                                   │
│  Call 1 → DB Schema LLM                                          │
│    Output: { tables[{ name, columns[{                             │
│               name, type, nullable, unique,                       │
│               primary_key, foreign_key }] }] }                    │
│  + sleep(4s)                                                      │
│                                                                   │
│  Call 2 → API Schema LLM                                         │
│    Output: { base_path, endpoints[{                               │
│               method, path, description,                          │
│               auth_required, roles_allowed[],                     │
│               request_body, response }] }                         │
│  + sleep(4s)                                                      │
│                                                                   │
│  Call 3 → UI Schema LLM                                          │
│    Output: { app_name, theme, pages[{                             │
│               name, route, auth_required,                         │
│               roles_allowed[], components[{                       │
│                 type, name, props[], api_endpoint }] }] }         │
│                                                                   │
│  Auth assembled directly from DesignSchema (no extra LLM call)   │
└──────────────────────────┬────────────────────────────────────────┘
                           │ db, api, ui, auth dicts
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│  STAGE 4 — Validation + Repair Engine      stage4_validate.py     │
│                                                                   │
│  for attempt in 1..MAX_REPAIR_ATTEMPTS:                           │
│    ┌─ validate_db(db) ────────────────────────────────────────┐  │
│    │  • every table has 'id' primary key                       │  │
│    │  • every table has 'created_at'                           │  │
│    │  • all foreign_key refs point to existing tables          │  │
│    └───────────────────────────────────────────────────────────┘  │
│    ┌─ validate_auth(auth) ────────────────────────────────────┐  │
│    │  • roles list is non-empty                                │  │
│    │  • role_permissions is present                            │  │
│    └───────────────────────────────────────────────────────────┘  │
│    ┌─ validate_api(api, db, auth) ────────────────────────────┐  │
│    │  • /auth/login endpoint exists                            │  │
│    │  • all roles_allowed values exist in auth.roles           │  │
│    └───────────────────────────────────────────────────────────┘  │
│    ┌─ validate_ui(ui, api, auth) ─────────────────────────────┐  │
│    │  • /login page exists                                     │  │
│    │  • component api_endpoint values map to real API paths    │  │
│    │  • all page roles_allowed exist in auth.roles             │  │
│    └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│    if errors found for layer X:                                   │
│      send targeted repair prompt (errors + broken schema)        │
│      replace only layer X — leave others untouched               │
│    if no errors → break early                                     │
└──────────────────────────┬────────────────────────────────────────┘
                           │ validated db, api, ui, auth + error log
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│  STAGE 5 — Code Generation (pure Python)   stage5_codegen.py      │
│                                                                   │
│  No LLM call — 100% deterministic from validated schemas          │
│                                                                   │
│  models.py      ← one SQLAlchemy ORM class per DB table           │
│  main.py        ← one FastAPI route stub per API endpoint         │
│  .env.example   ← DATABASE_URL, SECRET_KEY, TOKEN_EXPIRE          │
│  README.md      ← generated app README                           │
└──────────────────────────┬────────────────────────────────────────┘
                           │
                           ▼
         PipelineResult { job_id, status, app_schema,
           generated_code, validation_errors,
           repair_log, assumptions, metrics }
```

---

## 📁 Project Structure

```
ai-compiler/
│
├── backend/
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── stage1_intent.py       # LLM call → IntentSchema
│   │   ├── stage2_design.py       # LLM call → DesignSchema
│   │   ├── stage3_schemas.py      # 3× LLM calls → DB + API + UI schemas
│   │   ├── stage4_validate.py     # Cross-layer validation + repair loop
│   │   └── stage5_codegen.py      # Pure Python → models.py + main.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── intent_schema.py       # Pydantic v2: IntentSchema, Entity, UserRole, Feature
│   │   ├── db_schema.py           # Pydantic v2: DBSchema, Table, Column
│   │   ├── api_schema.py          # Pydantic v2: APISchema, Endpoint, RequestBody
│   │   ├── ui_schema.py           # Pydantic v2: UISchema, UIPage, UIComponent
│   │   ├── auth_schema.py         # Pydantic v2: AuthSchema, RolePermissions
│   │   └── app_schema.py          # Pydantic v2: AppSchema (composes all), PipelineResult
│   │
│   ├── utils/
│   │   └── llm_client.py          # Groq client: key rotation, retry-after, backoff
│   │
│   ├── orchestrator.py            # Wires all 5 stages → PipelineResult
│   ├── main.py                    # FastAPI: /generate, /metrics, /health + SQLite
│   ├── requirements.txt           # fastapi, uvicorn, openai, pydantic, dotenv
│   ├── Procfile                   # Railway deployment config
│   └── .env.example               # GROQ_API_KEYS, MAX_REPAIR_ATTEMPTS
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Full SPA: prompt input, pipeline animation, 8 tabs
│   │   ├── App.css                # Design system (CSS variables, dark theme)
│   │   └── index.css              # Global styles + Google Fonts
│   ├── public/
│   ├── vercel.json                # SPA rewrite: /* → /index.html
│   ├── tsconfig.json
│   └── package.json
│
├── evaluation/
│   └── evaluate.py                # 20-prompt harness, saves evaluation_results.json
│
├── .gitignore
└── README.md
```

---

## 🔬 Stage-by-Stage Deep Dive

### Stage 1 — Intent Extraction (`stage1_intent.py`)

The raw user prompt is sent to Groq with a strict system prompt. The LLM is instructed to extract structured intent and always satisfy these invariants:

- Always include a `users` entity
- Always include at least one role
- Never return empty `entities` or `roles`
- For vague input: make reasonable assumptions and document them

**System prompt contract:**
```
{
  "app_name": "string",
  "app_type": "string (e.g. CRM, E-commerce, Blog)",
  "entities": [{ "name", "attributes": [], "relationships": [] }],
  "roles":    [{ "name", "permissions": [] }],
  "features": [{ "name", "description", "requires_auth": bool }],
  "assumptions": [],
  "clarifications_needed": []
}
```

**Pydantic contract (`schemas/intent_schema.py`):**
```python
class Entity(BaseModel):
    name: str
    attributes: List[str]
    relationships: List[str] = []

class UserRole(BaseModel):
    name: str
    permissions: List[str]

class Feature(BaseModel):
    name: str
    description: str
    requires_auth: bool = False

class IntentSchema(BaseModel):
    app_name: str
    app_type: str
    entities: List[Entity]
    roles: List[UserRole]
    features: List[Feature]
    assumptions: List[str] = []
    clarifications_needed: List[str] = []
```

---

### Stage 2 — System Design (`stage2_design.py`)

Takes the full `IntentSchema` dict and produces a complete architecture design. The LLM is given the full intent JSON and instructed to enforce:

- Every entity must have an `id` primary key field
- Every entity must have a `created_at` datetime field
- The `users` entity must have `email`, `password_hash`, `role` fields
- Permissions must follow `resource:action` format (e.g. `contacts:read`)

**Output shape:**
```python
{
  "entities": [{ "name", "db_table", "fields": [{ "name", "type", "nullable", "unique", "primary_key", "foreign_key" }] }],
  "flows":    [{ "name", "steps": [], "roles_involved": [] }],
  "auth_design": { "type": "jwt", "roles": [], "role_permissions": [{ "role", "permissions": [] }] },
  "api_groups":  [{ "resource", "operations": ["list","create","read","update","delete"] }]
}
```

---

### Stage 3 — Schema Generation (`stage3_schemas.py`)

Three focused LLM calls. A compact context is built from the design output:

```python
context = {
    "app":        intent["app_name"],
    "entities":   [e["name"] for e in design["entities"]],
    "roles":      design["auth_design"]["roles"],
    "api_groups": [g["resource"] for g in design["api_groups"]],
    "features":   [f["name"] for f in intent["features"]],
}
```

Each call uses `response_format={"type": "json_object"}` — guaranteed parseable JSON.

| Call | System Prompt Focus | Output |
|---|---|---|
| DB Schema | Database architect — tables, columns, FK constraints | `{ tables: [{ name, columns[] }] }` |
| API Schema | REST API designer — endpoints, methods, role guards | `{ base_path, endpoints[] }` |
| UI Schema | UI architect — pages, components, route mapping | `{ app_name, theme, pages[] }` |

4-second sleep between each call to stay under Groq's 12k TPM per-key limit.

Auth schema is assembled directly from `DesignSchema.auth_design` — no extra LLM call needed.

---

### Stage 4 — Validation + Repair Engine (`stage4_validate.py`)

The most important stage. Enforces cross-layer consistency rules that no single LLM call could guarantee.

**All validation rules:**

| Layer | Rule | What's Checked |
|---|---|---|
| DB | `id` column | Every table must have an `id` integer primary key |
| DB | `created_at` column | Every table must have a `created_at` datetime column |
| DB | FK integrity | All `foreign_key` values must reference a table that exists in the schema |
| Auth | Non-empty roles | `auth.roles` must not be empty |
| Auth | Permissions present | `auth.role_permissions` must be present |
| API | Login endpoint | `/auth/login` (or any path containing "login") must exist |
| API | Role consistency | All `roles_allowed` on endpoints must exist in `auth.roles` |
| UI | Login page | A page with route `/login` or `/signin` must exist |
| UI | API path mapping | Every `component.api_endpoint` must map to a real API path (with path-param tolerance) |
| UI | Role consistency | All `page.roles_allowed` must exist in `auth.roles` |

**Repair loop (actual code logic):**
```python
for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
    db_errors   = validate_db(db)
    auth_errors = validate_auth(auth)
    api_errors  = validate_api(api, db, auth)
    ui_errors   = validate_ui(ui, api, auth)

    if not (db_errors + auth_errors + api_errors + ui_errors):
        break  # all clean — exit early

    # Repair only the broken layer — leave others untouched
    if db_errors:
        db, log = _repair_layer("db", db, db_errors, full_context)
    if auth_errors:
        auth, log = _repair_layer("auth", auth, auth_errors, full_context)
    if api_errors:
        api, log = _repair_layer("api", api, api_errors, full_context)
    if ui_errors:
        ui, log = _repair_layer("ui", ui, ui_errors, full_context)
```

Each `_repair_layer` call sends the specific errors + the broken layer JSON + full context to the LLM and replaces only that layer. This is **5× faster** than a full pipeline re-run.

---

### Stage 5 — Code Generation (`stage5_codegen.py`)

Zero LLM calls. Pure deterministic Python that templates code from the validated schemas.

**`models.py`** — SQLAlchemy ORM, one class per DB table:
```python
# Type mapping used internally
{
    "string":   "String(255)",
    "text":     "Text",
    "integer":  "Integer",
    "float":    "Float",
    "boolean":  "Boolean",
    "datetime": "DateTime",
}

# Example output for 'contacts' table
class Contact(Base):
    __tablename__ = 'contacts'
    id         = Column(Integer, primary_key=True, nullable=False)
    name       = Column(String(255), nullable=False)
    email      = Column(String(255), nullable=True)
    owner_id   = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, nullable=True)
```

**`main.py`** — FastAPI route stubs, one per endpoint:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Generated App')
app.add_middleware(CORSMiddleware, allow_origins=['*'], ...)

@app.post('/auth/login')
def post_auth_login():
    # TODO: implement
    return {"message": "TODO: implement /auth/login"}

@app.get('/contacts')
def get_contacts():
    # TODO: implement
    return {"message": "TODO: implement /contacts"}
```

**`.env.example`:**
```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=changeme
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🔐 Pydantic Schema Contracts

All data flowing between stages is strictly typed. If the LLM returns malformed JSON, Pydantic raises a `ValidationError`, which triggers the repair engine.

```
schemas/
├── intent_schema.py  →  IntentSchema
│                          ├── Entity(name, attributes[], relationships[])
│                          ├── UserRole(name, permissions[])
│                          └── Feature(name, description, requires_auth)
│
├── db_schema.py      →  DBSchema
│                          └── Table(name, columns[])
│                               └── Column(name, type, nullable, unique,
│                                          primary_key, foreign_key)
│
├── api_schema.py     →  APISchema
│                          └── Endpoint(method, path, description,
│                                       auth_required, roles_allowed[],
│                                       request_body, response)
│                               ├── RequestBody(fields[], required[])
│                               └── ResponseSchema(status_code, fields[])
│
├── ui_schema.py      →  UISchema
│                          └── UIPage(name, route, auth_required,
│                                    roles_allowed[], components[])
│                               └── UIComponent(type, name, props[],
│                                              api_endpoint)
│
├── auth_schema.py    →  AuthSchema
│                          └── RolePermissions(role, permissions[])
│
└── app_schema.py     →  AppSchema (composes all of the above)
                        PipelineResult(job_id, status, app_schema,
                          stage_outputs, validation_errors,
                          repair_log, assumptions, metrics)
```

---

## 🌐 LLM Client — Rate Limit Resilience (`utils/llm_client.py`)

Supports any number of Groq API keys via comma-separated `GROQ_API_KEYS` in `.env`. The client uses the OpenAI SDK pointed at Groq's OpenAI-compatible endpoint.

**Full retry / rotation logic:**
```
for attempt in 1 .. (MAX_RETRIES × num_keys):
    try:
        call Groq API with current key
        return (parsed_json, metrics)

    except RateLimitError:
        parse exact retry-after from error string  → "try again in 12.3s"
        wait (retry_after + 0.5s)
        rotate to next key
        if all keys exhausted:
            wait 30s extra, reset to key 0

    except AuthenticationError:
        key is invalid → rotate immediately

    except JSONDecodeError:
        retry up to MAX_RETRIES with 2s backoff
```

**All calls use:**
- `model = llama-3.3-70b-versatile` (Groq)
- `temperature = 0.2` — deterministic, reproducible
- `max_tokens = 1500` — focused, no padding
- `response_format = {"type": "json_object"}` — guaranteed parseable JSON
- `user_prompt` truncated to 3000 chars to stay under context limits

---

## 🖥️ Frontend (`frontend/src/App.tsx`)

React 19 + TypeScript SPA. No class components — all hooks. Monaco Editor (VS Code engine) for output display.

**UI layout:**
```
┌──────── Navbar: AICompiler · Beta · Groq status ────────────────┐
├──────── Hero: 5-stage pipeline progress animation ──────────────┤
│                                                                  │
│  ┌─── Sidebar ───────────┐  ┌─── Output Panel ─────────────┐   │
│  │ Textarea prompt input  │  │ [Full][Intent][DB][API]       │   │
│  │ Generate button        │  │ [UI][Auth][Code][Metrics]     │   │
│  │ Status pill + job_id   │  │                               │   │
│  │ 6 example prompts      │  │  Monaco Editor                │   │
│  │ Pipeline stage list    │  │  (JSON or Python, dark theme) │   │
│  │ Run metrics grid       │  │                               │   │
│  │ Validation errors      │  │  Repair log strip (if any)    │   │
│  │ Assumptions panel      │  │                               │   │
│  └────────────────────────┘  └───────────────────────────────┘   │
│                                                                  │
├──────── Footer: API Docs · Metrics · Health links ──────────────┤
└──────────────────────────────────────────────────────────────────┘
```

**8 output tabs:**

| Tab | Content |
|---|---|
| Full Schema | Complete `app_schema` JSON |
| Intent | `app_schema.intent` — entities, roles, features, assumptions |
| Database | `app_schema.database` — tables and columns |
| API | `app_schema.api` — all endpoints with auth rules |
| UI | `app_schema.ui` — pages, components, routes |
| Auth | `app_schema.auth` — JWT config, roles, permissions |
| Code | `generated_code` — `models.py`, `main.py`, `.env.example`, `README.md` |
| Metrics | `metrics` — latency, tokens, cost, repair attempts |

**6 one-click example prompts:**
- CRM with payments and analytics
- E-commerce with Stripe checkout
- Trello-style project management
- Hospital appointment booking
- SaaS invoicing with recurring billing
- Social media with follow system

**API key settings modal:**
- Supports Groq (free), OpenAI, OpenRouter
- Key stored only in `localStorage` — never sent to the server
- Provider selector with free/paid label

---

## 🧪 Evaluation Framework (`evaluation/evaluate.py`)

Runs 20 prompts through the full live pipeline. Measures and saves per-prompt stats.

**20 test prompts across 4 categories:**

| Category | Count | Examples |
|---|---|---|
| Real product | 10 | CRM, e-commerce, Trello, hospital, LMS, food delivery, invoicing, social, real estate, blog |
| Vague | 4 | "Build an app.", "I need a website", "Make it like Uber but different", "Build the next Facebook" |
| Conflicting | 3 | Free but paid, private but public, no-DB but persistent data |
| Incomplete | 3 | "Build something with users and products", "Add analytics to my app", "I want login and a dashboard" |

**Metrics captured per prompt:**
- `status` (success / partial / failed)
- `latency_seconds`
- `total_tokens`
- `repair_attempts`
- `validation_errors` count
- `assumptions_made` count
- `tables_generated`, `endpoints_generated`, `pages_generated`

**Aggregate summary output:**
```
==============================
EVALUATION SUMMARY
==============================
  Total:           20
  Success:         17  (85%)
  Failed:          3
  Avg Latency:     33.4s
  Total Cost:      $0.0
  Total Repairs:   4

  By Category:
    real        : 9/10  (90%)
    vague       : 3/4   (75%)
    conflicting : 2/3   (67%)
    incomplete  : 3/3   (100%)
```

**Results saved to `evaluation_results.json`.**

Run yourself:
```bash
cd evaluation
python evaluate.py
```

---

## 📡 API Reference

### `POST /generate`

**Request:**
```json
{ "prompt": "Build a CRM with login and contacts" }
```

Validation: prompt must be ≥ 10 characters.

**Response:**
```json
{
  "job_id": "a1b2c3d4",
  "status": "success | partial | failed",
  "app_schema": {
    "intent":   { "app_name": "...", "app_type": "...", "entities": [], "roles": [], "features": [], "assumptions": [] },
    "database": { "tables": [{ "name": "...", "columns": [] }] },
    "api":      { "base_path": "/api/v1", "endpoints": [] },
    "ui":       { "app_name": "...", "theme": "light", "pages": [] },
    "auth":     { "auth_type": "jwt", "roles": [], "role_permissions": [] }
  },
  "generated_code": {
    "models.py":    "from sqlalchemy import ...",
    "main.py":      "from fastapi import ...",
    ".env.example": "DATABASE_URL=...",
    "README.md":    "# App Name ..."
  },
  "stage_outputs":     { "stage1_intent": {}, "stage2_design": {}, ... },
  "validation_errors": [],
  "repair_log":        [],
  "assumptions":       [],
  "metrics": {
    "total_latency_seconds": 34.2,
    "total_tokens": 6800,
    "estimated_cost_usd": 0.0,
    "repair_attempts": 0,
    "stages": [
      { "stage": "intent_extraction", "latency_seconds": 3.1, "total_tokens": 820 },
      { "stage": "system_design",     "latency_seconds": 4.2, "total_tokens": 1100 },
      ...
    ]
  }
}
```

---

### `GET /metrics`

Returns aggregated stats across all pipeline runs stored in SQLite:

```json
{
  "total_runs":    42,
  "success_rate":  88.1,
  "avg_latency":   33.4,
  "total_repairs": 7,
  "runs": [
    {
      "job_id": "a1b2c3d4",
      "prompt": "Build a CRM...",
      "status": "success",
      "provider": "groq",
      "latency_seconds": 34.2,
      "total_tokens": 6800,
      "repair_attempts": 0,
      "validation_errors": 0,
      "created_at": 1718000000.0
    }
  ]
}
```

---

### `GET /health`
```json
{ "status": "ok", "provider": "groq", "model": "llama-3.3-70b-versatile" }
```

### `GET /docs`
Auto-generated Swagger UI — fully interactive, lists all routes, request/response schemas.

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| Backend | Python + FastAPI | 3.12 / 0.111 | Type-safe, async-ready, auto-docs |
| Data validation | Pydantic v2 | 2.7.1 | Strict typing for all inter-stage contracts |
| LLM | Groq API — llama-3.3-70b-versatile | — | Free tier, 70B quality, fast inference |
| LLM client | OpenAI SDK | 1.30.1 | OpenAI-compatible — works with Groq, OpenAI, OpenRouter |
| Metrics DB | SQLite (built-in) | — | Zero-config, no external service |
| Frontend | React 19 + TypeScript | 19 / 5.x | Type-safe, hooks-only SPA |
| Code editor | Monaco Editor (`@monaco-editor/react`) | — | VS Code engine, JSON + Python syntax |
| Icons | Lucide React | — | Consistent, tree-shakeable |
| HTTP client | Axios | — | Promise-based, interceptor support |
| Backend deploy | Railway | — | Free tier, Procfile auto-detection |
| Frontend deploy | Vercel | — | Free tier, SPA rewrite via `vercel.json` |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Free Groq API key → [console.groq.com](https://console.groq.com) (no credit card)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add your GROQ_API_KEYS (comma-separated for rotation)
python -m uvicorn main:app --reload --port 8080
# API available at http://localhost:8080
# Swagger docs at http://localhost:8080/docs
```

### Frontend
```bash
cd frontend
npm install
# Create frontend/.env:
echo "REACT_APP_API_URL=http://localhost:8080" > .env
npm start
# UI available at http://localhost:3000
```

### Evaluation
```bash
cd evaluation
python evaluate.py
# Runs all 20 prompts against the live pipeline
# Saves full results → evaluation/evaluation_results.json
```

---

## 🔑 Environment Variables

### Backend `.env`
```env
# Comma-separated Groq keys — auto-rotates on 429 rate limit
# Get free keys (no credit card): https://console.groq.com
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3,gsk_key4

# Max repair attempts per pipeline run (default: 3)
MAX_REPAIR_ATTEMPTS=3
```

### Frontend `.env`
```env
REACT_APP_API_URL=http://localhost:8080
```

---

## 🚀 Deployment

### Backend → Railway
1. Push repo to GitHub
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set root directory: `backend`
4. Add env vars: `GROQ_API_KEYS`, `MAX_REPAIR_ATTEMPTS`
5. Railway reads `Procfile` → runs `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Copy the generated Railway URL

### Frontend → Vercel
1. [vercel.com](https://vercel.com) → New Project → Import repo
2. Set root directory: `frontend`
3. Add env var: `REACT_APP_API_URL=https://your-railway-url.up.railway.app`
4. Vercel reads `vercel.json` → rewrites all routes to `index.html` (SPA support)

---

## 🧩 Key Design Decisions

| Decision | Chosen | Alternative | Reason |
|---|---|---|---|
| LLM generation | Multi-stage pipeline | Single mega-prompt | Isolated errors, focused prompts, targeted repair |
| Repair strategy | Targeted per-layer | Full pipeline re-run | 5× faster, cheaper, more reliable |
| JSON enforcement | `response_format=json_object` | Prompt-only instruction | Guarantees parseable JSON on every call |
| Temperature | `0.2` | `0.7+` | Deterministic, reproducible output |
| Code generation | Pure Python (Stage 5) | LLM-generated code | Zero hallucinations, fully deterministic |
| Rate limit handling | Key rotation + exact retry-after | Simple exponential backoff | Zero downtime with multiple free keys |
| Auth assembly | From Stage 2 design (no extra LLM call) | Separate LLM call | Saves tokens + latency, design already has full auth |
| LLM provider | Groq (free tier) | OpenAI GPT-4o | $0 cost for demo; llama-3.3-70b quality is sufficient |
| Metrics DB | SQLite | PostgreSQL | Zero-config, no external service needed |
| User prompt cap | 3000 chars | No cap | Prevents context overflow, keeps LLM responses focused |

---

## 📊 Rate Limit Strategy

With 4 Groq free-tier keys:
- ~57,600 requests/day total capacity
- Auto-rotation on `429` — zero downtime
- Exact `retry-after` parsed from error message: `"try again in 12.3s"` → wait `12.8s`
- If all keys exhausted → extra 30s wait → restart from key 0
- 4-second inter-call delay in Stage 3 to stay under 12k TPM per key
- 4-second delay between pipeline stages in orchestrator

---

## 👤 Author

Built by **Tushar Sahu** for the Base44 AI Engineer Internship Task.

- GitHub: [github.com/sahutushar](https://github.com/sahutushar)
- Repo: [AI-Compiler---NL-to-App-Schema](https://github.com/sahutushar/AI-Compiler---NL-to-App-Schema)
