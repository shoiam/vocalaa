from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from supabase.client import ClientOptions
from models import *
from dotenv import load_dotenv
import os
import uvicorn
from loguru import logger
import sys
from auth_utils import create_access_token, get_current_user
from database import get_supabase_client
from utils import generate_unique_mcp_slug
from cache_service import cache_get, cache_set, cache_delete, generate_cache_key

load_dotenv()

logger.remove()

# Console logging (stderr)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# File logging - General application logs
logger.add(
    "logs/vocalaa.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="10 MB",  # Create new file when current reaches 10MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip"  # Compress old log files
)

# File logging - Error logs only
logger.add(
    "logs/vocalaa_errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="5 MB",
    retention="60 days",
    compression="zip"
)

# File logging - MCP specific logs
logger.add(
    "logs/mcp_requests.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="5 MB",
    retention="7 days",
    compression="zip",
    filter=lambda record: "MCP" in record["message"] or record["name"] == "mcp"
)

supabase_client = get_supabase_client()
app = FastAPI(
    title="Vocalaa API",
    description="Interactive professional information server",
    version="0.1.0"
)

# Add CORS middleware
# Get allowed origins from environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,https://vocalaa.com").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]  # Remove any whitespace

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers including Authorization
)


@app.get("/health")
async def health():
    """Detailed health check."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "Vocalaa API"
    }

@app.post("/auth/login")
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

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Protected route - requires valid JWT token"""
    logger.info(f"User info requested for: {current_user['email']}")
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "message": "Token is valid"
    }

@app.post("/auth/register")
async def auth(user_data: UserRegister):
    """User Registration"""
    logger.info(f"Registration attempt for email: {user_data.email}")
    logger.debug(f"User data received: {user_data}")
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
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

@app.get("/profile/me")
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

@app.put("/profile/update")
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

@app.post("/profile/create")
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

@app.delete("/profile/delete")
async def delete_profile(current_user: dict = Depends(get_current_user)):
    """Delete the current user's profile"""
    logger.info(f"Deleting profile for user: {current_user['email']}")

    try:
        # Check if profile exists
        existing_response = supabase_client.table("profiles").select("*").eq("user_id", current_user["user_id"]).execute()

        if not existing_response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        existing_profile = existing_response.data[0]
        mcp_slug = existing_profile['mcp_slug']

        # Delete the profile
        response = supabase_client.table("profiles").delete().eq("user_id", current_user["user_id"]).execute()

        if response.data:
            logger.info(f"Profile deleted for user: {current_user['email']}, MCP slug: {mcp_slug}")

            # Invalidate cache for both user_id and mcp_slug lookups
            user_cache_key = generate_cache_key("profile", current_user["user_id"])
            mcp_cache_key = generate_cache_key("profile_slug", mcp_slug)
            cache_delete(user_cache_key)
            cache_delete(mcp_cache_key)
            logger.info(f"Cache invalidated for deleted profile: {current_user['email']}")

            return {
                "message": "Profile deleted successfully",
                "mcp_slug": mcp_slug
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to delete profile")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/{user_slug}")
@app.options("/mcp/{user_slug}")
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
    
async def handle_mcp_request(request_data: dict, user_profile: dict) -> dict:
    """Handle MCP JSON-RPC requests with user profile data"""
    
    method = request_data.get("method")
    request_id = request_data.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": f"vocalaa-{user_profile['mcp_slug']}",
                    "version": "0.1.0"
                },
                "instructions": "This server provides professional information and background."
            }
        }
    
    elif method == "tools/list":
        tools = [
            {
                "name": "get_basic_info",
                "description": "Get basic personal information and contact details",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_work_experience", 
                "description": "Get professional work history and achievements",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_skills",
                "description": "Get technical and soft skills",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    elif method == "tools/call":
        tool_name = request_data.get("params", {}).get("name")
        return await handle_tool_call(tool_name, user_profile, request_id)
    
    else:
        return {
            "jsonrpc": "2.0", 
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
async def handle_tool_call(tool_name: str, user_profile: dict, request_id: int) -> dict:
    """Execute MCP tool calls with user profile data"""
    
    try:
        if tool_name == "get_basic_info":
            basic_info = user_profile.get("basic_info", {})
            response_text = f"""**{basic_info.get('name', 'Name not set')}**
{basic_info.get('title', 'Title not set')}
📍 {basic_info.get('location', 'Location not set')}

**Contact:**
📧 {basic_info.get('email', 'Email not set')}

**Summary:**
{basic_info.get('summary', 'Summary not set')}"""

        elif tool_name == "get_work_experience":
            work_exp = user_profile.get("work_experience", [])
            if not work_exp:
                response_text = "No work experience data available."
            else:
                response_text = "**Professional Experience:**\n\n"
                for job in work_exp:
                    response_text += f"**{job.get('role')}** at **{job.get('company')}**\n"
                    response_text += f"📅 {job.get('duration')}\n\n"
                    response_text += f"{job.get('description')}\n\n"
                    
                    if job.get('achievements'):
                        response_text += "**Key Achievements:**\n"
                        for achievement in job['achievements']:
                            response_text += f"• {achievement}\n"
                        response_text += "\n"
                    
                    response_text += "---\n\n"

        elif tool_name == "get_skills":
            skills = user_profile.get("skills", {})
            if not skills:
                response_text = "No skills data available."
            else:
                response_text = "**Technical & Professional Skills:**\n\n"
                for category, skill_list in skills.items():
                    if skill_list:
                        category_name = category.replace('_', ' ').title()
                        response_text += f"**{category_name}:**\n"
                        if isinstance(skill_list, list):
                            response_text += f"{', '.join(skill_list)}\n\n"

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": response_text
                }]
            }
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)}
        }
    
# Removed handle_mcp_sse_connection - MCP uses JSON-RPC over POST, not SSE
def main():
    """Run the Http server"""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
