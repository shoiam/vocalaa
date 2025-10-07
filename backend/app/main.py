import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    """Run the HTTP server"""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()