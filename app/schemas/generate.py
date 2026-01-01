from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class GenerateRequest(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    use_case: Optional[str] = None
    requirements: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None

    # NEW
    prompt: Optional[str] = None

class GenerateResponse(BaseModel):
    id: str
    result: Dict[str, Any]  # architecture JSON, diagrams, folder structure
    zip_url: str
