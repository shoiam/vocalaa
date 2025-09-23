import pytest
from database import get_supabase_client

class TestDatabase:
    
    def test_supabase_client_creation(self):
        """Test that Supabase client can be created."""
        client = get_supabase_client()
        assert client is not None
        assert hasattr(client, 'auth')
        assert hasattr(client, 'table')
    
    
    def test_supabase_client_type(self, supabase_client):
        """Test that client is the correct type."""
        from supabase._sync.client import SyncClient
        assert isinstance(supabase_client, SyncClient)