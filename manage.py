#!/usr/bin/env python3
"""
AIOS Kernel Manager
This script is the central entry point for managing the AIOS Kernel and its applications.
Use it to start the server, run tests, or execute management commands.
"""

import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# --- Configuration ---
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True

def setup_environment():
    """Sets up the execution environment."""
    # Load environment variables from .env
    load_dotenv()
    
    # Add project root and core_kernel/src to sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    core_src = os.path.join(project_root, "core_kernel", "src")
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if core_src not in sys.path:
        sys.path.insert(0, core_src)
        
    # Ensure logs directory exists at root level for easier access
    os.makedirs(os.path.join(project_root, "logs"), exist_ok=True)

def run_server(host=HOST, port=PORT, reload=RELOAD):
    """Starts the FastAPI server."""
    print(f"🚀 Starting AIOS Kernel on http://{host}:{port}")
    # We import app here to ensure sys.path is set up first
    try:
        # Check if we can import the app
        from core_kernel.src.main import app
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        # Try importing as 'main' if core_kernel.src is in path directly
        try:
            from main import app
        except ImportError as e2:
            print(f"❌ Critical error: Could not import 'app' from main.py: {e2}")
            sys.exit(1)
            
    uvicorn.run("core_kernel.src.main:app", host=host, port=port, reload=reload)

def run_tests():
    """Runs the test suite using pytest."""
    try:
        import pytest
        print("🧪 Running tests...")
        sys.exit(pytest.main(["-v", "tests"]))
    except ImportError:
        print("❌ pytest is not installed. Please install it with: pip install pytest")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AIOS Kernel Management Script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run Server Command
    run_parser = subparsers.add_parser("runserver", help="Start the AIOS Kernel server")
    run_parser.add_argument("--host", default=HOST, help=f"Bind host (default: {HOST})")
    run_parser.add_argument("--port", type=int, default=PORT, help=f"Bind port (default: {PORT})")
    run_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    # Run Tests Command
    test_parser = subparsers.add_parser("test", help="Run the test suite")

    args = parser.parse_args()
    
    setup_environment()

    if args.command == "runserver":
        run_server(host=args.host, port=args.port, reload=not args.no_reload)
    elif args.command == "test":
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
