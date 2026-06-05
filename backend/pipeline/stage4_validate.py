"""
Validation + Repair Engine
Checks cross-layer consistency and repairs specific broken layers.
"""
import json
import os
from typing import List
from utils.llm_client import call_llm

MAX_REPAIR_ATTEMPTS = int(os.getenv("MAX_REPAIR_ATTEMPTS", 3))


# ── helpers ──────────────────────────────────────────────────────────────────

def _all_db_columns(db: dict) -> set[str]:
    cols = set()
    for table in db.get("tables", []):
        for col in table.get("columns", []):
            cols.add(f"{table['name']}.{col['name']}")
    return cols


def _all_api_paths(api: dict) -> set[str]:
    return {ep["path"] for ep in api.get("endpoints", [])}


def _all_auth_roles(auth: dict) -> set[str]:
    return set(auth.get("roles", []))


# ── layer validators ──────────────────────────────────────────────────────────

def validate_db(db: dict) -> List[str]:
    errors = []
    tables = db.get("tables")
    if not tables:
        errors.append("DB: 'tables' list is missing or empty")
        return errors
    table_names = {t["name"] for t in tables}
    for table in tables:
        cols = [c["name"] for c in table.get("columns", [])]
        if "id" not in cols:
            errors.append(f"DB table '{table['name']}' missing 'id' primary key column")
        if "created_at" not in cols:
            errors.append(f"DB table '{table['name']}' missing 'created_at' column")
        for col in table.get("columns", []):
            fk = col.get("foreign_key")
            if fk:
                ref_table = fk.split(".")[0]
                if ref_table not in table_names:
                    errors.append(f"DB: foreign key '{fk}' references non-existent table '{ref_table}'")
    return errors


def validate_api(api: dict, db: dict, auth: dict) -> List[str]:
    errors = []
    endpoints = api.get("endpoints")
    if not endpoints:
        errors.append("API: 'endpoints' list is missing or empty")
        return errors
    paths = [ep["path"] for ep in endpoints]
    if "/auth/login" not in paths and not any("login" in p for p in paths):
        errors.append("API: missing login endpoint")
    roles = _all_auth_roles(auth)
    for ep in endpoints:
        for role in ep.get("roles_allowed", []):
            if role and role not in roles:
                errors.append(f"API endpoint '{ep['path']}' references undefined role '{role}'")
    return errors


def validate_ui(ui: dict, api: dict, auth: dict) -> List[str]:
    errors = []
    pages = ui.get("pages")
    if not pages:
        errors.append("UI: 'pages' list is missing or empty")
        return errors
    api_paths = _all_api_paths(api)
    roles = _all_auth_roles(auth)
    has_login = any(p.get("route") in ["/login", "/signin"] for p in pages)
    if not has_login:
        errors.append("UI: missing login page at /login")
    for page in pages:
        for role in page.get("roles_allowed", []):
            if role and role not in roles:
                errors.append(f"UI page '{page['name']}' references undefined role '{role}'")
        for comp in page.get("components", []):
            ep = comp.get("api_endpoint")
            if ep and ep not in api_paths:
                # soft warning — endpoint path might use path params
                base = ep.split("{")[0].rstrip("/")
                if not any(p.startswith(base) for p in api_paths):
                    errors.append(f"UI component '{comp['name']}' maps to unknown API endpoint '{ep}'")
    return errors


def validate_auth(auth: dict) -> List[str]:
    errors = []
    if not auth.get("roles"):
        errors.append("Auth: 'roles' list is missing or empty")
    if not auth.get("role_permissions"):
        errors.append("Auth: 'role_permissions' is missing")
    return errors


# ── repair ────────────────────────────────────────────────────────────────────

def _repair_layer(layer_name: str, broken_json: dict, errors: List[str], context: dict) -> tuple[dict, str]:
    repair_prompt = f"""Fix the following {layer_name} JSON schema.
Errors found:
{chr(10).join(f'- {e}' for e in errors)}
Current schema:
{json.dumps(broken_json, indent=2)}
Context:
{json.dumps(context, indent=2)}
Return ONLY the corrected {layer_name} JSON schema."""
    fixed, _ = call_llm(
        "You are a schema repair engine. Fix JSON schemas. Return only valid corrected JSON.",
        repair_prompt,
        stage_name=f"repair_{layer_name}"
    )
    return fixed, f"Repaired {layer_name}: {len(errors)} errors fixed"


def run(db: dict, api: dict, ui: dict, auth: dict) -> tuple[dict, dict, dict, dict, List[str], List[str]]:
    """
    Validate all layers, repair broken ones (up to MAX_REPAIR_ATTEMPTS).
    Returns (db, api, ui, auth, all_errors, repair_log).
    """
    all_errors: List[str] = []
    repair_log: List[str] = []

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        db_errors   = validate_db(db)
        auth_errors = validate_auth(auth)
        api_errors  = validate_api(api, db, auth)
        ui_errors   = validate_ui(ui, api, auth)

        round_errors = db_errors + auth_errors + api_errors + ui_errors
        if not round_errors:
            break

        all_errors.extend(round_errors)
        context = {"db": db, "api": api, "ui": ui, "auth": auth}

        if db_errors:
            db,   log = _repair_layer("db",   db,   db_errors,   context)
            repair_log.append(f"[attempt {attempt}] {log}")
        if auth_errors:
            auth, log = _repair_layer("auth", auth, auth_errors, context)
            repair_log.append(f"[attempt {attempt}] {log}")
        if api_errors:
            api,  log = _repair_layer("api",  api,  api_errors,  context)
            repair_log.append(f"[attempt {attempt}] {log}")
        if ui_errors:
            ui,   log = _repair_layer("ui",   ui,   ui_errors,   context)
            repair_log.append(f"[attempt {attempt}] {log}")

    return db, api, ui, auth, all_errors, repair_log
