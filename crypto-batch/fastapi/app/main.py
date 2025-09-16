from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin_auth import router as admin_auth_router
from app.api.routes.admin_user import router as admin_user_router
from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as user_router
from app.core.database import health_check as health_check_db

app = FastAPI(root_path="/api")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI 🚀"}

@app.get("/health")
async def health_check():
    return await health_check_db()


app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(admin_user_router, prefix="/admin/users", tags=["admin_users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_auth_router, prefix="/admin/auth", tags=["admin_auth"])