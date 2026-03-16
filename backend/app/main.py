from fastapi import FastAPI

from app.api.routers.ai_router import router as ai_router

app = FastAPI()

app.include_router(ai_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

