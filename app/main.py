from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, users, records, dashboard, audit_logs

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Data Processing and Access Control API",
    description="Backend system for managing financial records with robust user role management.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Finance API"}
