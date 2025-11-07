from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.aicode_service import generate_code, generate_unit_tests, generate_documentation
from backend.services.file_handler import copy_to_clipboard, save_to_file
from backend.models.schemas import (
    CodeGenerationRequest, CodeGenerationResponse,
    TestGenerationRequest, TestGenerationResponse,
    DocumentationRequest, DocumentationResponse,
    FileOperationRequest, FileOperationResponse
)
from backend.config.settings import settings

app = FastAPI(title="AI Code Generator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code_endpoint(request: CodeGenerationRequest):
    """Generate code based on user query and language."""
    try:
        code = generate_code(request.query, request.language)
        return CodeGenerationResponse(code=code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-tests", response_model=TestGenerationResponse)
async def generate_tests_endpoint(request: TestGenerationRequest):
    """Generate unit tests for the provided code."""
    try:
        tests = generate_unit_tests(request.code, request.language)
        return TestGenerationResponse(tests=tests)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-documentation", response_model=DocumentationResponse)
async def generate_documentation_endpoint(request: DocumentationRequest):
    """Generate documentation for the provided code."""
    try:
        documentation = generate_documentation(request.code, request.language)
        return DocumentationResponse(documentation=documentation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/copy-to-clipboard", response_model=FileOperationResponse)
async def copy_to_clipboard_endpoint(request: FileOperationRequest):
    """Copy code to clipboard."""
    try:
        message = copy_to_clipboard(request.code)
        return FileOperationResponse(message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-to-file", response_model=FileOperationResponse)
async def save_to_file_endpoint(request: FileOperationRequest):
    """Save code to file."""
    try:
        message = save_to_file(request.code, request.language or "txt")
        return FileOperationResponse(message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
