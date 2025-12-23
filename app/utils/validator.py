# def validate_scaffold(data):
#     if "structure" not in data:
#         raise ValueError("Missing structure field")

#     structure = data["structure"]

#     if not isinstance(structure, list) or len(structure) < 5:
#         raise ValueError("Invalid scaffold output. Structure must contain multiple paths")


def validate_scaffold(result: dict):
    """
    Temporary validator.
    Will be expanded later with strict schema checks.
    """
    if "system_design" not in result:
        raise ValueError("Missing system_design")

    if "component_tree" not in result:
        raise ValueError("Missing component_tree")

    if "folders" not in result["component_tree"]:
        raise ValueError("component_tree must contain folders")

    return True
