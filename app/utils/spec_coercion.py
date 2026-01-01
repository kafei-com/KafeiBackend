def coerce_architecture_spec(data: dict) -> dict:
    """
    Fix common LLM type mismatches BEFORE Pydantic validation.
    """
    if "requirements" in data and isinstance(data["requirements"], str):
        data["requirements"] = [
            r.strip()
            for r in data["requirements"].split("\n")
            if r.strip()
        ]

    if "tech_stack" in data and isinstance(data["tech_stack"], str):
        data["tech_stack"] = [
            t.strip()
            for t in data["tech_stack"].split(",")
            if t.strip()
        ]

    if "use_case" in data and isinstance(data["use_case"], list):
        data["use_case"] = " ".join(data["use_case"])

    return data
