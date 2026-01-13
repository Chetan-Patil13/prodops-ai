from fastapi import APIRouter, HTTPException
from app.auth.auth_service import authenticate_user
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(email: str):
    user = authenticate_user(email)

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
