from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers.search_router import router as search_router
from backend.app.api.routers.test_generation_router import router as test_generation_router
from backend.app.api.routers.ai_router import router as ai_router
from backend.app.api.routers.stats import router as stats_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,

    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)

app.include_router(test_generation_router)
app.include_router(ai_router)
app.include_router(stats_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}

