import json
from utils.llm_client import call_llm

SYSTEM_PROMPT = """You are a senior software architect. Given structured app intent, design the full system architecture.
Return ONLY valid JSON matching this exact schema:
{
  "entities": [
    {
      "name": "string",
      "db_table": "string",
      "fields": [
        { "name": "string", "type": "string", "nullable": true/false, "unique": false, "primary_key": false, "foreign_key": "table.column or null" }
      ]
    }
  ],
  "flows": [
    { "name": "string", "steps": ["string"], "roles_involved": ["string"] }
  ],
  "auth_design": {
    "type": "jwt",
    "roles": ["string"],
    "role_permissions": [
      { "role": "string", "permissions": ["resource:action"] }
    ]
  },
  "api_groups": [
    { "resource": "string", "operations": ["list", "create", "read", "update", "delete"] }
  ]
}
Rules:
- Every entity must have an 'id' field as primary_key
- Every entity must have 'created_at' datetime field
- User entity must have email, password_hash, role fields
- Permissions format: "resource:action" e.g. "contacts:read", "contacts:write"
"""


def run(intent: dict) -> tuple[dict, dict]:
    return call_llm(SYSTEM_PROMPT, f"Design system architecture for this intent:\n\n{json.dumps(intent, indent=2)}", stage_name="system_design")
