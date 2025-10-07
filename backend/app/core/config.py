import os
from dotenv import load_dotenv

load_dotenv()

# CORS Configuration
def get_allowed_origins():
    """Get allowed origins from environment variable"""
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,https://vocalaa.com").split(",")
    return [origin.strip() for origin in allowed_origins]

# Server Configuration
PORT = int(os.getenv("PORT", 8000))

# MCP Configuration
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "https://mcp.vocalaa.com")
