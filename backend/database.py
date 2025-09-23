import os
import threading
from typing import Optional
from queue import Queue
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class SupabaseManager:
    _instance: Optional['SupabaseManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.url: str = os.getenv("SUPABASE_URL")
            self.key: str = os.getenv("SUPABASE_KEY")
            self._connection_pool = Queue(maxsize=10)
            self._active_connections = 0
            self._pool_lock = threading.Lock()
            self._initialized = True
            self._create_initial_connections()
    
    def _create_initial_connections(self):
        for _ in range(3):
            client = self._create_client()
            if client:
                self._connection_pool.put(client)
                self._active_connections += 1
    
    def _create_client(self) -> Optional[Client]:
        try:
            options = ClientOptions(
                schema="public",
                postgrest_client_timeout=10,
                storage_client_timeout=10
            )
            client = create_client(
                supabase_url=self.url,
                supabase_key=self.key,
                options=options
            )
            return client
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            return None
    
    def get_client(self) -> Optional[Client]:
        with self._pool_lock:
            if not self._connection_pool.empty():
                return self._connection_pool.get()
            elif self._active_connections < 10:
                client = self._create_client()
                if client:
                    self._active_connections += 1
                    return client
        return None
    
    def return_client(self, client: Client):
        with self._pool_lock:
            if not self._connection_pool.full():
                self._connection_pool.put(client)
    
    def get_connection_stats(self) -> dict:
        with self._pool_lock:
            return {
                'active_connections': self._active_connections,
                'available_in_pool': self._connection_pool.qsize(),
                'max_connections': 10
            }

supabase_manager = SupabaseManager()

def get_supabase_client() -> Optional[Client]:
    return supabase_manager.get_client()

def return_supabase_client(client: Client):
    supabase_manager.return_client(client)

def dbConnection():
    client = get_supabase_client()
    if not client:
        logger.error("Failed to get Supabase client from pool")
        return False
    
    try:
        response = client.auth.get_session()
        logger.info("Supabase connection successful!")
        logger.debug(f"Client initialized: {type(client)}")
        logger.debug(f"Connection pool stats: {supabase_manager.get_connection_stats()}")
        return_supabase_client(client)
        return True
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        return_supabase_client(client)
        return False

if __name__ == "__main__":
    dbConnection()