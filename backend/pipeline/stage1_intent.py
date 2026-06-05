from utils.llm_client import call_llm

SYSTEM_PROMPT = """You are an expert software architect. Extract structured intent from user prompts.
Return ONLY valid JSON matching this exact schema:
{
  "app_name": "string",
  "app_type": "string (e.g. CRM, E-commerce, Blog, Dashboard)",
  "entities": [
    { "name": "string", "attributes": ["string"], "relationships": ["string"] }
  ],
  "roles": [
    { "name": "string", "permissions": ["string"] }
  ],
  "features": [
    { "name": "string", "description": "string", "requires_auth": true/false }
  ],
  "assumptions": ["string"],
  "clarifications_needed": ["string"]
}
Rules:
- Always include a 'users' entity
- Always include at least one role
- If prompt is vague, make reasonable assumptions and list them in 'assumptions'
- Never return empty entities or roles
"""


def run(user_prompt: str) -> tuple[dict, dict]:
    return call_llm(SYSTEM_PROMPT, f"Extract intent from this prompt:\n\n{user_prompt}", stage_name="intent_extraction")
