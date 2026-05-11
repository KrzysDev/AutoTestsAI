from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers.search_router import router as search_router
from backend.app.api.routers.test_generation_router import router as test_generation_router
from backend.app.api.routers.ai_router import router as ai_router
from backend.app.api.routers.stats_router import router as stats_router
from backend.app.api.routers.fixing_router import router as fixing_router
from backend.app.api.routers.auth_router import router as auth_router


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
app.include_router(fixing_router)
app.include_router(auth_router)


@app.get("/")
async def read_root():
    print("Root endpoint hit!")
    return {"Hello": "World"}

