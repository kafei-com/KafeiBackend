def validate_scaffold(data):
    if "structure" not in data:
        raise ValueError("Missing structure field")

    structure = data["structure"]

    if not isinstance(structure, list) or len(structure) < 5:
        raise ValueError("Invalid scaffold output. Structure must contain multiple paths")
