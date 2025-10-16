"""Test utilities and helper functions"""
import time

# Global variable to track last registration time to avoid rate limits
_last_registration_time = 0
_min_registration_interval = 1.5  # Minimum seconds between registrations


def rate_limited_register(client, register_data):
    """
    Helper function to register with rate limiting across all tests.

    Ensures a minimum interval between registration requests to avoid
    hitting Supabase rate limits during test execution.

    Args:
        client: FastAPI TestClient instance
        register_data: Dictionary with registration data (email, password, etc.)

    Returns:
        Response from the registration endpoint
    """
    global _last_registration_time

    # Calculate time since last registration
    current_time = time.time()
    time_since_last = current_time - _last_registration_time

    # If not enough time has passed, wait
    if time_since_last < _min_registration_interval:
        wait_time = _min_registration_interval - time_since_last
        time.sleep(wait_time)

    # Make registration request
    response = client.post("/auth/register", json=register_data)
    _last_registration_time = time.time()

    return response
