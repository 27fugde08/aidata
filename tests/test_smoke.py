from fastapi.testclient import TestClient
import sys
import os

# Add project root to path so we can import core_kernel
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core_kernel', 'src')))

try:
    from core_kernel.src.main import app
except ImportError:
    # Fallback if the first import fails (e.g. running from root)
    try:
        from main import app
    except ImportError:
        # Last resort if running via manage.py which sets paths differently
        from core_kernel.src.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
