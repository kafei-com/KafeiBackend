from pydantic import BaseModel
from typing import List

class ArchitectureSpec(BaseModel):
    project_name: str
    description: str
    use_case: str
    requirements: List[str]
    tech_stack: List[str]

    inferred: bool = False  # important metadata
