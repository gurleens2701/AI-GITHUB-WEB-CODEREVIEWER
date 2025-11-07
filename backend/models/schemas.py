from pydantic import BaseModel
from typing import Optional

class CodeGenerationRequest(BaseModel):
    query: str
    language: str

class CodeGenerationResponse(BaseModel):
    code: str

class TestGenerationRequest(BaseModel):
    code: str
    language: str

class TestGenerationResponse(BaseModel):
    tests: str

class DocumentationRequest(BaseModel):
    code: str
    language: str

class DocumentationResponse(BaseModel):
    documentation: str

class FileOperationRequest(BaseModel):
    code: str
    language: Optional[str] = None

class FileOperationResponse(BaseModel):
    message: str
