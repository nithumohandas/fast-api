from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
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


# Sub APP with DB

# Database configuration
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# SQLAlchemy setup
class Base(DeclarativeBase):
    pass

# Global session maker
async_session_maker = None


@asynccontextmanager
async def lifespan(sub_app: FastAPI):
    # Startup: Create engine and session maker
    global async_session_maker

    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        pool_pre_ping=True,  # Verify connections before using
    )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Optionally create tables
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    print("Database connected!")

    yield  # Application runs here

    # Shutdown: Close engine
    await engine.dispose()
    print("Database disconnected!")


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Create FastAPI app with lifespan
sub_app = FastAPI(lifespan=lifespan)


# Example route using the database
@sub_app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Use the session here
    # result = await db.execute(select(User).where(User.id == user_id))
    # user = result.scalar_one_or_none()
    return {"user_id": user_id}
