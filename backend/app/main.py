from fastapi import FastAPI

from backend.app.api.routers.ai_router import router as ai_router
from backend.app.api.routers.search_router import router as search_router
from backend.app.api.routers.test_generation_router import router as test_generation_router
from backend.app.api.routers.json_test_converting_router import router as json_test_converting_router

app = FastAPI()

app.include_router(ai_router)
app.include_router(search_router)
app.include_router(test_generation_router)
app.include_router(json_test_converting_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

