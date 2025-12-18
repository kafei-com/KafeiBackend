from pydantic import BaseModel
from typing import Any, Dict, List

class GenerateRequest(BaseModel):
    project_name: str
    description: str
    tech_stack: List[str]
    requirements: str
    use_case: str

class GenerateResponse(BaseModel):
    id: str
    result: Dict[str, Any]  # architecture JSON, diagrams, folder structure
    zip_url: str
