from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = None

    # 🔐 Auth
    hashed_password: Optional[str] = None   # <-- allow NULL
    oauth_provider: Optional[str] = None    # google, github
    oauth_sub: Optional[str] = None         # provider user id

    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
