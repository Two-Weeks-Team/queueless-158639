import os
import json
import re
from typing import Any, Dict, List
import httpx

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
INFERENCE_ENDPOINT = "https://inference.do-ai.run/v1/chat/completions"
API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

# ---------------------------------------------------------------------------
# Helper to extract JSON from LLM responses (markdown, code fences, etc.)
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

# ---------------------------------------------------------------------------
# Core inference call – single place for HTTP, timeout, parsing, and fallback
# ---------------------------------------------------------------------------
def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            resp = await client.post(INFERENCE_ENDPOINT, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Expected structure: {"choices": [{"message": {"content": "..."}}]}
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            return json.loads(json_str)
        except Exception as e:
            # Any problem – return a graceful fallback
            return {"note": "AI service temporarily unavailable.", "error": str(e)}

# ---------------------------------------------------------------------------
# Public AI‑powered helpers used by route handlers
# ---------------------------------------------------------------------------
async def predict_wait_time(location_id: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are an expert restaurant operations analyst. Predict the wait time in minutes for the given location based only on its identifier. Return a JSON object with a single key `wait_time` as an integer."},
        {"role": "user", "content": f"Location ID: {location_id}"},
    ]
    result = await _call_inference(messages)
    # Ensure the key exists; if not, fallback to a generic response
    if isinstance(result, dict) and "wait_time" in result:
        return {"wait_time": result["wait_time"]}
    return {"note": "Could not calculate wait time at this moment."}

async def get_recommendations(customer_id: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are a friendly restaurant chatbot that suggests up to three menu items for a customer while they wait. Provide a JSON array under the key `recommendations` containing short dish names."},
        {"role": "user", "content": f"Customer ID: {customer_id}"},
    ]
    result = await _call_inference(messages)
    if isinstance(result, dict) and "recommendations" in result:
        return {"recommendations": result["recommendations"]}
    return {"note": "No recommendations available right now."}
