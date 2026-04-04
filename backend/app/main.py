from fastapi import FastAPI

<<<<<<< Updated upstream
from backend.app.api.routers.ai_router import router as ai_router
from backend.app.api.routers.search_router import router as search_router
from backend.app.api.routers.test_generation_router import router as test_generation_router
from backend.app.api.routers.json_test_converting_router import router as json_test_converting_router
=======
from app.api.routers.ai_router import router as ai_router
from app.api.routers.search_router import router as search_router
from app.api.routers.generator_router import router as generator_router
>>>>>>> Stashed changes

app = FastAPI()

app.include_router(ai_router)
app.include_router(search_router)
<<<<<<< Updated upstream
app.include_router(test_generation_router)
app.include_router(json_test_converting_router)
=======
app.include_router(generator_router)
>>>>>>> Stashed changes

@app.get("/")
def read_root():
    return {"Hello": "World"}

