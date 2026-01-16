from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.auth.auth_service import authenticate_user
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# -------------------------
# Request schema
# -------------------------
class LoginRequest(BaseModel):
    email: str


# -------------------------
# Login route
# -------------------------
@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(payload.email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token = create_access_token(
        {
            "user_id": user["id"],
            "email": user["user_email"],
            "roles": user["roles"],
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["user_email"],
            "roles": user["roles"],
        },
    }
