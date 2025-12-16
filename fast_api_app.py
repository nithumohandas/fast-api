from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import secure_api
from routers import travel_destinations

app = FastAPI(
    title="Remote API Service",
    description="Service that validates JWT tokens from auth server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(secure_api.router)
app.include_router(travel_destinations.router)

@app.get("/")
async def root():
    return {
        "service": "Remote API Service",
        "auth": "JWT tokens from auth server",
        "endpoints": {
            "protected_local": "/api/protected-local",
            "protected_remote": "/api/protected-remote",
            "data": "/api/data"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}