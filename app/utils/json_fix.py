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
