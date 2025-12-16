from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth

app = FastAPI(
    title="JWT Authentication Service",
    description="Centralized authentication service for microservices",
    version="1.0.0"
)

# Enable CORS for remote servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "service": "JWT Authentication Service",
        "endpoints": {
            "login": "/auth/login",
            "register": "/auth/register",
            "validate": "/auth/validate",
            "refresh": "/auth/refresh",
            "public_key": "/auth/public-key"
        }
    }