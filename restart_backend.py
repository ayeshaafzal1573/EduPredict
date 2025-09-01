#!/usr/bin/env python3
"""
Simple script to restart the backend server
"""
import subprocess
import sys
import os

def restart_backend():
    """Restart the backend server"""
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.getcwd(), 'backend')
        os.chdir(backend_dir)
        
        # Start the server
        cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload']
        print(f"Starting backend server with command: {' '.join(cmd)}")
        
        # Run the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    restart_backend()
