from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
import os
from app.models.profile import ProfileCreate
from app.core.security import get_current_user
from app.core.database import get_supabase_client
from app.utils.slug import generate_unique_mcp_slug
from app.core.cache import cache_get, cache_set, cache_delete, generate_cache_key

router = APIRouter(prefix="/profile", tags=["Profile"])
supabase_client = get_supabase_client()

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's profile"""
    logger.info(f"Getting profile for user: {current_user['email']}")

    # Check cache first
    cache_key = generate_cache_key("profile", current_user["user_id"])
    cached_profile = cache_get(cache_key)

    if cached_profile:
        logger.info(f"Profile retrieved from cache for user: {current_user['email']}")
        return cached_profile

    try:
        response = supabase_client.table("profiles").select("*").eq("user_id", current_user["user_id"]).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = response.data[0]
        logger.info(f"Profile found in database with MCP slug: {profile['mcp_slug']}")

        profile_data = {
            "profile_id": profile["id"],
            "mcp_slug": profile["mcp_slug"],
            "mcp_url": f"{os.getenv('MCP_BASE_URL', 'https://mcp.vocalaa.com')}/mcp/{profile['mcp_slug']}",
            "basic_info": profile["basic_info"],
            "work_experience": profile["work_experience"],
            "skills": profile["skills"],
            "projects": profile["projects"],
            "education": profile["education"],
            "created_at": profile["created_at"]
        }

        # Cache the profile data for 30 minutes
        cache_set(cache_key, profile_data, ttl=1800)

        return profile_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update")
async def update_profile(profile_data: ProfileCreate, current_user: dict = Depends(get_current_user)):
    """Update an existing user's profile"""
    logger.info(f"Updating profile for user: {current_user['email']}")

    try:
        # Check if profile exists
        existing_response = supabase_client.table("profiles").select("*").eq("user_id", current_user["user_id"]).execute()

        if not existing_response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        existing_profile = existing_response.data[0]

        # Update the profile record
        updated_profile = {
            "basic_info": profile_data.basic_info.model_dump(),
            "work_experience": [exp.model_dump() for exp in profile_data.work_experience],
            "skills": profile_data.skills.model_dump(),
            "projects": [proj.model_dump() for proj in profile_data.projects],
            "education": [edu.model_dump() for edu in profile_data.education]
        }

        response = supabase_client.table("profiles").update(updated_profile).eq("user_id", current_user["user_id"]).execute()

        if response.data:
            logger.info(f"Profile updated for MCP slug: {existing_profile['mcp_slug']}")

            # Invalidate cache for both user_id and mcp_slug lookups
            user_cache_key = generate_cache_key("profile", current_user["user_id"])
            mcp_cache_key = generate_cache_key("profile_slug", existing_profile['mcp_slug'])
            cache_delete(user_cache_key)
            cache_delete(mcp_cache_key)
            logger.info(f"Cache invalidated for user: {current_user['email']}")

            return {
                "message": "Profile updated successfully",
                "mcp_slug": existing_profile["mcp_slug"],
                "mcp_url": f"{os.getenv('MCP_BASE_URL', 'https://mcp.vocalaa.com')}/mcp/{existing_profile['mcp_slug']}",
                "profile_id": response.data[0]["id"]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update profile")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_profile(profile_data: ProfileCreate, current_user: dict = Depends(get_current_user)):
    logger.info(f"Creating profile for user: {current_user['email']}")

    try:
        mcp_slug = await generate_unique_mcp_slug(profile_data.basic_info.name)

        profile_record = {
            "user_id": current_user["user_id"],
            "mcp_slug": mcp_slug,
            "basic_info": profile_data.basic_info.model_dump(),
            "work_experience": [exp.model_dump() for exp in profile_data.work_experience],
            "skills": profile_data.skills.model_dump(),
            "projects": [proj.model_dump() for proj in profile_data.projects],
            "education": [edu.model_dump() for edu in profile_data.education]
        }

        response = supabase_client.table("profiles").insert(profile_record).execute()

        if response.data:
            logger.info(f"Profile created with MCP slug: {mcp_slug}")

            # Invalidate any potential cached data for this user
            user_cache_key = generate_cache_key("profile", current_user["user_id"])
            cache_delete(user_cache_key)
            logger.info(f"Cache invalidated for new profile: {current_user['email']}")

            return {
                "message": "Profile created successfully",
                "mcp_slug": mcp_slug,
                "mcp_url": f"{os.getenv('MCP_BASE_URL', 'https://mcp.vocalaa.com')}/mcp/{mcp_slug}",
                "profile_id": response.data[0]["id"]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create profile")
    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
