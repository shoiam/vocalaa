import secrets
import string
import re
from database import get_supabase_client, return_supabase_client

async def generate_unique_mcp_slug(preferred_name: str) ->  str:
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', preferred_name.lower())
    if len(clean_name) > 15:
        clean_name = clean_name[:15]
    
    chars = string.ascii_lowercase + string.digits

    for attempt in range(10):
        random_suffix = ''.join(secrets.choice(chars) for _ in range(7))
        proposed_slug = f"{clean_name}-{random_suffix}"

        try:
            supabase_client = get_supabase_client()
            response = supabase_client.table("profiles").select("id").eq("mcp_slug", proposed_slug).execute()
            if not response.data:
                return proposed_slug
            return_supabase_client(supabase_client)
        except Exception:
            pass
    
    return ''.join(secrets.choice(chars) for _ in range(15))