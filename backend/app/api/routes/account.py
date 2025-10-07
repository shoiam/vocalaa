from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from app.core.security import get_current_user
from app.core.database import get_supabase_client
from app.core.cache import cache_delete, generate_cache_key


router = APIRouter(prefix="/account", tags=["Account"])
supabase_client = get_supabase_client()

@router.delete("/delete")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete the current user's account and all associated data"""
    logger.info(f"Deleting account for user: {current_user['email']}")

    try:
        mcp_slug = None

        # First, check if profile exists and get the mcp_slug
        try:
            existing_response = supabase_client.table("profiles").select("*").eq("user_id", current_user["user_id"]).execute()
            if existing_response.data:
                mcp_slug = existing_response.data[0]['mcp_slug']

                # Delete the profile first
                profile_delete = supabase_client.table("profiles").delete().eq("user_id", current_user["user_id"]).execute()
                if profile_delete.data:
                    logger.info(f"Profile deleted for user: {current_user['email']}, MCP slug: {mcp_slug}")

                    # Invalidate cache
                    user_cache_key = generate_cache_key("profile", current_user["user_id"])
                    mcp_cache_key = generate_cache_key("profile_slug", mcp_slug)
                    cache_delete(user_cache_key)
                    cache_delete(mcp_cache_key)
        except Exception as e:
            logger.warning(f"Profile deletion failed or no profile exists: {str(e)}")

        # Delete the user account from Supabase Auth
        try:
            auth_response = supabase_client.auth.admin.delete_user(current_user["user_id"])
            logger.info(f"User account deleted: {current_user['email']}")
        except Exception as e:
            logger.error(f"Failed to delete user account: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete user account")

        return {
            "message": "Account and all associated data deleted successfully",
            "email": current_user["email"],
            "mcp_slug": mcp_slug
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))