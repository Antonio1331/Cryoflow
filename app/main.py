from fastapi import FastAPI
from app.api.endpoints import router as cryo_router

app = FastAPI(title="CryoFlow API", version="1.0.0")

# Подключаем роутер
app.include_router(cryo_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to CryoFlow API. NASA Space Apps Challenge 2026."}