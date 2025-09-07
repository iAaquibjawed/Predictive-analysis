from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token from Rails backend
    """
    try:
        token = credentials.credentials

        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user information
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role", "patient")
        exp: int = payload.get("exp")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing expiration"
            )

        # Return user context
        return {
            "user_id": user_id,
            "role": user_role,
            "token": token
        }

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """
    Get current authenticated user
    """
    return token_data

def require_role(required_role: str):
    """
    Decorator to require specific user role
    """
    def role_checker(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
        user_role = token_data.get("role")

        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )

        return token_data

    return role_checker

def require_roles(required_roles: list):
    """
    Decorator to require one of several user roles
    """
    def role_checker(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
        user_role = token_data.get("role")

        if user_role not in required_roles and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
            )

        return token_data

    return role_checker

