#!/usr/bin/env python3
"""
Script to start both backend and frontend services for the AI Code Generator.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if requirements.txt dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import gradio
        import openai
        import pyperclip
        import pydantic
        import requests
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if environment file exists."""
    env_file = Path("env.example")
    if not env_file.exists():
        print("❌ env.example file not found")
        return False
    
    print("📝 Please copy env.example to .env and add your OpenAI API key:")
    print("   cp env.example .env")
    print("   # Then edit .env file with your OpenAI API key")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.app:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--reload"
    ])
    return backend_process

def start_frontend():
    """Start the Gradio frontend server."""
    print("🎨 Starting frontend server...")
    frontend_process = subprocess.Popen([
        sys.executable, "frontend/app.py"
    ])
    return frontend_process

def main():
    """Main function to start both services."""
    print("🔧 AI Code Generator - Service Starter")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment file
    check_env_file()
    
    try:
        # Start backend
        backend_process = start_backend()
        
        # Wait a bit for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n✅ Both services started successfully!")
        print("🔗 Backend API: http://127.0.0.1:8000")
        print("🎨 Frontend UI: http://127.0.0.1:7819")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("\n⚠️  Press Ctrl+C to stop both services")
        
        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            print("✅ Services stopped successfully!")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
