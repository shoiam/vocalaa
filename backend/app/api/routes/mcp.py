from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from app.core.database import get_supabase_client
from app.core.cache import cache_get, cache_set, generate_cache_key
from app.services.mcp_service import handle_mcp_request

router = APIRouter(prefix="/mcp", tags=["MCP"])
supabase_client = get_supabase_client()

@router.post("/{user_slug}")
@router.options("/{user_slug}")
async def user_mcp_endpoint(user_slug: str, request: Request):
    logger.info(f"MCP request for user: {user_slug}, method: {request.method}")

    try:
        if request.method == "OPTIONS":
            return JSONResponse(content={"status": "ok"})

        # Only handle POST requests for MCP JSON-RPC
        if request.method != "POST":
            raise HTTPException(405, f"Method {request.method} not allowed for MCP endpoint")

        # Check cache first
        cache_key = generate_cache_key("profile_slug", user_slug)
        cached_profile = cache_get(cache_key)

        if cached_profile:
            logger.info(f"Profile retrieved from cache for slug: {user_slug}")
            user_profile = cached_profile
        else:
            response = supabase_client.table("profiles").select("*").eq("mcp_slug", user_slug).execute()

            if not response.data:
                raise HTTPException(404, f"MCP server not found for: {user_slug}")

            user_profile = response.data[0]
            # Cache profile for 30 minutes
            cache_set(cache_key, user_profile, ttl=1800)
            logger.info(f"Profile cached for slug: {user_slug}")

        # Handle MCP JSON-RPC request
        data = await request.json()
        logger.info(f"MCP JSON-RPC request: {data}")
        result = await handle_mcp_request(data, user_profile)
        logger.info(f"MCP JSON-RPC response: {result}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP endpoint error: {str(e)}")
        logger.exception("Full exception traceback:")
        raise HTTPException(500, str(e))