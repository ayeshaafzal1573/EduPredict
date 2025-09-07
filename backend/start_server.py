#!/usr/bin/env python3
"""
Script to start the EduPredict backend server
"""

import uvicorn
import os
import sys
from loguru import logger

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 8000))
        logger.info("Starting EduPredict Backend Server...")
        logger.info(f"Server will be available at: http://127.0.0.1:{port}")
        logger.info(f"API Documentation: http://127.0.0.1:{port}/docs")
        logger.info("Press CTRL+C to stop the server")
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)