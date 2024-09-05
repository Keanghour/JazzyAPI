from fastapi import FastAPI
from app.api.auth.admin.routes import router as admin_router
from app.database.database import init_db

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(admin_router, prefix="/v1/auth/admin/api")
