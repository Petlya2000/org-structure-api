import logging
from fastapi import FastAPI
from app.api.routers import departments, employees
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Organizational Structure API")
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])
@app.get("/")
async def root():
    return {"message": "Organizational Structure API", "docs": "/docs"}
