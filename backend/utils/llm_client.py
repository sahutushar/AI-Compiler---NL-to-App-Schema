import os
import json
import time
import re
from openai import OpenAI, RateLimitError, AuthenticationError
from dotenv import load_dotenv

load_dotenv(override=True)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL    = "llama-3.3-70b-versatile"
MAX_RETRIES   = 5


def _load_keys() -> list[str]:
    """Load all Groq keys from env. Supports comma-separated list."""
    raw = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", ""))
    keys = [k.strip() for k in raw.split(",") if k.strip() and len(k.strip()) > 10]
    if not keys:
        raise ValueError("No valid GROQ_API_KEYS found in .env")
    return keys


def call_llm(
    system_prompt: str,
    user_prompt: str,
    stage_name: str = "",
    api_key: str = None,   # accepted but ignored — server keys always used
    provider: str = None,
) -> tuple[dict, dict]:
    load_dotenv(override=True)
    keys      = _load_keys()
    key_index = 0

    user_prompt = user_prompt[:3000]

    for attempt in range(1, MAX_RETRIES * len(keys) + 1):
        current_key = keys[key_index % len(keys)]
        client      = OpenAI(api_key=current_key, base_url=GROQ_BASE_URL)

        try:
            start    = time.time()
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            )
            latency = round(time.time() - start, 2)
            usage   = response.usage
            raw     = response.choices[0].message.content.strip()
            raw     = re.sub(r"^```(?:json)?\s*", "", raw)
            raw     = re.sub(r"\s*```$",           "", raw)

            return json.loads(raw), {
                "stage":             stage_name,
                "latency_seconds":   latency,
                "prompt_tokens":     usage.prompt_tokens     if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens":      usage.total_tokens      if usage else 0,
                "estimated_cost_usd": 0.0,
                "key_index":         key_index,
            }

        except RateLimitError as e:
            wait = _parse_retry_after(str(e))
            print(f"[{stage_name}] Key #{key_index} rate limited. Waiting {wait}s then rotating...")
            time.sleep(wait)
            # Rotate to next key
            key_index += 1
            if key_index >= len(keys):
                # All keys exhausted for this round — wait longer then retry from key 0
                key_index = 0
                extra_wait = 30
                print(f"[{stage_name}] All {len(keys)} key(s) exhausted. Waiting {extra_wait}s...")
                time.sleep(extra_wait)
            if attempt >= MAX_RETRIES * len(keys):
                raise RuntimeError(
                    f"All {len(keys)} Groq key(s) are rate limited. "
                    "Add more keys to GROQ_API_KEYS in .env or wait a minute."
                )

        except AuthenticationError:
            print(f"[{stage_name}] Key #{key_index} is invalid. Rotating...")
            key_index += 1
            if key_index >= len(keys):
                raise RuntimeError("All Groq keys are invalid. Check GROQ_API_KEYS in .env.")

        except json.JSONDecodeError:
            if attempt >= MAX_RETRIES:
                raise ValueError(f"Stage '{stage_name}' returned invalid JSON after {MAX_RETRIES} attempts")
            time.sleep(2)


def _parse_retry_after(error_msg: str) -> float:
    try:
        match = re.search(r"try again in ([\d.]+)s", error_msg)
        if match:
            return float(match.group(1)) + 0.5
    except Exception:
        pass
    return 5.0
