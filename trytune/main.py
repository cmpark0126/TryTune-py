from fastapi import FastAPI
from trytune.routers import pipelines, models

# uvicorn fastapi.main:app --host 0.0.0.0 --port 80 --log-level trace
app = FastAPI()

app.include_router(pipelines.router)
app.include_router(models.router)
