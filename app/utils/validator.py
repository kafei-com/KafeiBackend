def validate_scaffold(result: dict):
    """
    Validator supporting PARTIAL_SUCCESS mode.
    System design is mandatory.
    Component tree is optional.
    """

    # System design is REQUIRED
    if "system_design" not in result or not result["system_design"]:
        raise ValueError("Missing system_design")

    # Component tree is OPTIONAL
    component_tree = result.get("component_tree")

    if component_tree is not None:
        if not isinstance(component_tree, dict):
            raise ValueError("component_tree must be an object")

        if "folders" not in component_tree:
            raise ValueError("component_tree must contain 'folders'")

        if not isinstance(component_tree["folders"], list):
            raise ValueError("'folders' must be a list")

    return True
