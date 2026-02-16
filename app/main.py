from fastapi import FastAPI
from app.api.users import router as users_router

app = FastAPI(title="User Management API")

app.include_router(users_router)


@app.get("/health")
def health_check():
    return {"status": "Wow, I feel good"}
