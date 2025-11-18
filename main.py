# app/main.py
from fastapi import FastAPI
from api import dataAnalytics, uploadFiles

app = FastAPI(title="FastAPI Data Analytics for excel file")

app.include_router(uploadFiles.router, prefix="/api", tags=["File Upload"])
app.include_router(dataAnalytics.router, prefix="/api", tags=["Data Analytics"])
