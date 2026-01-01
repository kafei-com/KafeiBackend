import json
import re

def safe_json_loads(text: str):
    # Remove outer code fences like ```json or ```
    cleaned = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # Attempt removing nested fences inside values
        cleaned = re.sub(r"```mermaid|```", "", cleaned, flags=re.IGNORECASE).strip()
        return json.loads(cleaned)


def extract_json(text: str) -> str:
    """
    Extracts the first valid JSON object or array from an LLM response.

    Handles:
    - Leading / trailing text
    - ```json code blocks
    - Extra explanations before or after JSON
    """

    if not text:
        raise ValueError("Empty response from LLM")

    # 1️⃣ Remove markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()

    # 2️⃣ Try to find the first JSON object or array
    match = re.search(
        r"(\{[\s\S]*\}|\[[\s\S]*\])",
        cleaned
    )

    if not match:
        raise ValueError("No JSON found in LLM response")

    return match.group(1)