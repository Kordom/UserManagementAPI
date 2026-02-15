from fastapi import FastAPI

app = FastAPI(title="User Management API")


@app.get("/health")
def health_check():
    return {"status": "Wow, I feel good"}

