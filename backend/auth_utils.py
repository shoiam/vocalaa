from jose import JWTError, ExpiredSignatureError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
load_dotenv()
security = HTTPBearer()

def create_access_token(user_id: str, email: str)->str:
    if not user_id or not email:
        raise Exception("Invalid user_id or email. Please try again after fixing this.")
    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    jwt_string = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
    return jwt_string

def verify_token(token: str) -> dict:
    if not token:
        raise ValueError("Token is required")
    
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise ValueError("Invalid token: missing user ID")
            
        return {"user_id": user_id, "email": email}
        
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        user_data = verify_token(token)
        return user_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )