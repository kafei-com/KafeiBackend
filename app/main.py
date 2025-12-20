# main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routes.generate import router as generate_router
from app.services.generation_service import GenerationService 
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.core.docs import scalar_docs
# Assuming GenerationService is still imported and contains the LLMProvider

# Global variable to hold the initialized service instance
global_generation_service: GenerationService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic (Connect/Initialize) ---
    print("Starting up resources...")
    init_db()
    
    # Initialize the GenerationService, which initializes LLMProvider
    global global_generation_service
    global_generation_service = GenerationService()
    
    yield # The application runs here
    
    # --- Shutdown Logic (The Cleanup) ---
    print("Initiating graceful shutdown for all services.")
    
    # Call the shutdown method on the LLMProvider instance
    # The GenerationService holds the LLMProvider instance.
    if global_generation_service:
        await global_generation_service.llm.shutdown() 
    
    print("Cleanup complete. Ready to exit.")

# Pass the lifespan context manager to the FastAPI app
app = FastAPI(title="Kafei Backend", lifespan=lifespan, docs_url=None, redoc_url=None)

# ... (include router logic, potentially updating it to use the global_generation_service)
@app.get("/docs", include_in_schema=False)
def docs():
    return scalar_docs()

app.include_router(generate_router, prefix="/generate")
app.include_router(auth_router)
app.include_router(users_router)

# testing new branch push