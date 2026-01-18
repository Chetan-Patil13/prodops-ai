from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import decode_token
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get current authenticated user"""
    try:
        payload = decode_token(credentials.credentials)
        logger.info(f"User authenticated: {payload.get('email')} with roles {payload.get('roles')}")
        return payload
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(*required_roles):
    """Decorator to require specific roles"""
    def role_checker(current_user = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        
        if not any(role in user_roles for role in required_roles):
            logger.warning(f"Access denied for user {current_user.get('email')} - required roles: {required_roles}")
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role(s): {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


# Specific role requirements
def supervisor_only(current_user = Depends(get_current_user)):
    """Require SUPERVISOR role"""
    if "SUPERVISOR" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Supervisor access required")
    return current_user


def maintenance_or_supervisor(current_user = Depends(get_current_user)):
    """Require MAINTENANCE or SUPERVISOR role"""
    user_roles = current_user.get("roles", [])
    if not any(role in user_roles for role in ["MAINTENANCE", "SUPERVISOR"]):
        raise HTTPException(
            status_code=403, 
            detail="Maintenance or Supervisor access required"
        )
    return current_user