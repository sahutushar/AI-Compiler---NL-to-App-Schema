import json
import time
from utils.llm_client import call_llm

DB_SYSTEM_PROMPT = """You are a database architect. Generate a complete DB schema from system design.
Return ONLY valid JSON:
{
  "tables": [
    {
      "name": "string",
      "columns": [
        {
          "name": "string",
          "type": "string|integer|boolean|datetime|text|float",
          "nullable": true/false,
          "unique": false,
          "primary_key": false,
          "foreign_key": "table.column or null"
        }
      ]
    }
  ]
}
Rules:
- Every table must have an 'id' integer primary_key column
- Every table must have 'created_at' datetime column
- Foreign keys must reference existing tables
- Use snake_case for all names
"""

API_SYSTEM_PROMPT = """You are a REST API designer. Generate complete API schema from system design.
Return ONLY valid JSON:
{
  "base_path": "/api/v1",
  "endpoints": [
    {
      "method": "GET|POST|PUT|DELETE",
      "path": "string",
      "description": "string",
      "auth_required": true/false,
      "roles_allowed": ["string"],
      "request_body": { "fields": ["string"], "required": ["string"] } or null,
      "response": { "status_code": 200, "fields": ["string"] }
    }
  ]
}
Rules:
- Always include POST /auth/login and POST /auth/register
- Use RESTful naming: /resources, /resources/{id}
- Auth endpoints have auth_required: false
- All other endpoints have auth_required: true
"""

UI_SYSTEM_PROMPT = """You are a UI architect. Generate complete UI schema from system design.
Return ONLY valid JSON:
{
  "app_name": "string",
  "theme": "light",
  "pages": [
    {
      "name": "string",
      "route": "string",
      "auth_required": true/false,
      "roles_allowed": ["string"],
      "components": [
        {
          "type": "form|table|card|button|input|chart|navbar|sidebar",
          "name": "string",
          "props": ["string"],
          "api_endpoint": "string or null"
        }
      ]
    }
  ]
}
Rules:
- Always include Login page at route /login with auth_required: false
- Always include a Dashboard page
- Each component with api_endpoint must reference a real API path
- Use PascalCase for page and component names
"""


def run(design: dict, intent: dict) -> tuple[dict, dict, dict, dict, dict, dict]:
    entities   = [e.get("name") for e in design.get("entities", [])]
    roles      = design.get("auth_design", {}).get("roles", [])
    api_groups = [g.get("resource") for g in design.get("api_groups", [])]
    context    = json.dumps({
        "app":        intent.get("app_name"),
        "entities":   entities,
        "roles":      roles,
        "api_groups": api_groups,
        "features":   [f.get("name") for f in intent.get("features", [])],
    })
    db,  db_m  = call_llm(DB_SYSTEM_PROMPT,  f"Generate DB schema for:\n{context}",  "schema_gen_db")
    time.sleep(4)
    api, api_m = call_llm(API_SYSTEM_PROMPT, f"Generate API schema for:\n{context}", "schema_gen_api")
    time.sleep(4)
    ui,  ui_m  = call_llm(UI_SYSTEM_PROMPT,  f"Generate UI schema for:\n{context}",  "schema_gen_ui")
    return db, api, ui, db_m, api_m, ui_m
