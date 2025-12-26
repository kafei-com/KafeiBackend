MAX_RETRIES = 3

TEMPERATURE_SEQUENCE = [
    0.2,  # normal
    0.1,  # more deterministic
    0.0   # strict
]

PRIMARY_MODEL = "gemini"
FALLBACK_MODEL = "groq"