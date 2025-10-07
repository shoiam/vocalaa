from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from app.models.auth import UserLogin, UserRegister
from app.core.security import create_access_token, get_current_user
from app.core.database import get_supabase_client


router = APIRouter(prefix="/auth", tags=["Authentication"])
supabase_client = get_supabase_client()


@router.post("/login")
async def login(user_data: UserLogin):
    logger.info(f"Login attempt for email: {user_data.email}")
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        if response.user:
            access_token = create_access_token(
                user_id=response.user.id,
                email=response.user.email
            )
            logger.info(f"Login successful for user: {response.user.id}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": response.user.id,
                "email": response.user.email
            }
        else:
            logger.error("Login failed - Invalid credentials.")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Login Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Protected route - requires valid JWT token"""
    logger.info(f"User info requested for: {current_user['email']}")
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "message": "Token is valid"
    }

@router.post("/register")
async def auth(user_data: UserRegister):
    """User Registration"""
    logger.info(f"Registration attempt for email: {user_data.email}")
    logger.debug(f"User data received: {user_data}")
    # url: str = os.getenv("SUPABASE_URL")
    # key: str = os.getenv("SUPABASE_KEY")
    try:
        logger.info("Calling Supabase auth.sign_up...")
        response = supabase_client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        logger.debug(f"Supabase response: {response}")
        if response.user:
            logger.info(f"User registered successfully with ID: {response.user.id}")
            return {
                "message": "User registered successful",
                "user_id": response.user.id,
                "email": response.user.email
            }
        else:
            logger.error("Registration failed - no user in response")
            logger.debug(f"Full response: {response}")
            raise HTTPException(status_code=400, detail="Registration failed")
    except Exception as e:
        logger.error(f"Invalid input: {str(e)}")
        logger.exception("Full exception details: ")
        raise HTTPException(status_code=422, detail=str(e))