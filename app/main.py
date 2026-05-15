import logging
from fastapi import FastAPI
from app.api.routers import departments, employees

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Organizational Structure API",
    description="API for managing departments and employees",
    version="1.0.0"
)

# Include routers
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Organizational Structure API", "docs": "/docs"}

@app.on_event("startup")
async def startup():
    logging.info("Starting up the application")

@app.on_event("shutdown")
async def shutdown():
    logging.info("Shutting down the application")
