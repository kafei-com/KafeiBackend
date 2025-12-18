from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.1-8b-instant"
    LLM_PROVIDER: str = "groq"
    SECRET_KEY: str | None = None
    DB_PASSWORD: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
