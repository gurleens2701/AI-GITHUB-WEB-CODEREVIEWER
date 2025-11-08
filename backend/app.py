from fastapi import FastAPI, HTTPException, Request, Header
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

# NEW IMPORTS for webhook functionality
from backend.services.git_service import github_service
from backend.services.review_service import review_service
from typing import Optional

app = FastAPI(title="AI Code Generator & Review API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXISTING ENDPOINTS (Keep all your current functionality)
# ============================================================================

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


# ============================================================================
# NEW WEBHOOK ENDPOINTS (GitHub Integration)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - system status."""
    return {
        "message": "AI Code Review System is running!",
        "version": "2.0.0",
        "features": [
            "Code Generation",
            "Unit Test Generation", 
            "Documentation Generation",
            "GitHub PR Code Review (via webhook)"
        ]
    }


@app.get("/status")
async def system_status():
    """Check system configuration status."""
    return {
        "openai_configured": settings.openai_api_key is not None,
        "github_configured": settings.github_token is not None,
        "webhook_configured": settings.github_webhook_secret is not None,
        "backend_url": f"http://{settings.backend_host}:{settings.backend_port}"
    }


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint for PR code reviews.
    
    FLOW:
    1. GitHub sends PR event → This endpoint
    2. Verify signature (security)
    3. Parse PR data
    4. Fetch code changes
    5. AI reviews code
    6. Post review back to GitHub
    
    MOBILE DEV ANALOGY:
    Like receiving a push notification, verifying it's real,
    processing the data, and sending a response back.
    """
    
    try:
        # STEP 1: Get raw request body for signature verification
        payload_body = await request.body()
        
        print("📥 Webhook received from GitHub")
        
        # STEP 2: Verify this request actually came from GitHub
        try:
            github_service.verify_webhook_signature(
                payload_body=payload_body,
                signature_header=x_hub_signature_256
            )
            print("✅ Webhook signature verified")
        except ValueError as e:
            print(f"❌ Signature verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # STEP 3: Parse the JSON payload
        payload = await request.json()

        print(f"🔍 DEBUG - Webhook Action: {payload.get('action', 'NO ACTION')}")
        print(f"🔍 DEBUG - Event Keys: {list(payload.keys())}")
        print(f"🔍 DEBUG - Has pull_request? {'pull_request' in payload}")

        # STEP 4: Extract PR information
        pr_data = github_service.parse_webhook_pr(payload)
        
        # STEP 4: Extract PR information
        pr_data = github_service.parse_webhook_pr(payload)
        
        if not pr_data:
            return {"message": "❌ Invalid webhook payload"}
        
        print(f"📋 PR Data: {pr_data}")
        
        # STEP 5: Check if this is a PR event we care about
        action = pr_data["action"]
        if action not in ["opened", "synchronize", "reopened"]:
            # "synchronize" = PR updated with new commits
            # We only review when PR is opened or updated
            return {
                "message": f"⏭️  Ignoring action: {action}",
                "action": action
            }
        
        print(f"🔍 Processing PR #{pr_data['pr_number']} - Action: {action}")
        
        # STEP 6: Fetch PR diff (the actual code changes)
        try:
            pr_diff = github_service.get_pr_diff(
                repo_owner=pr_data["repo_owner"],
                repo_name=pr_data["repo_name"],
                pr_number=pr_data["pr_number"]
            )
            print(f"📄 Fetched diff: {len(pr_diff)} characters")
        except Exception as e:
            print(f"❌ Failed to fetch diff: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch PR diff: {e}")
        
        # STEP 7: Fetch PR files metadata
        try:
            pr_files = github_service.get_pr_files(
                repo_owner=pr_data["repo_owner"],
                repo_name=pr_data["repo_name"],
                pr_number=pr_data["pr_number"]
            )
            print(f"📂 Files changed: {len(pr_files)}")
        except Exception as e:
            print(f"❌ Failed to fetch files: {e}")
            pr_files = []
        
        # STEP 8: AI reviews the code
        print("🤖 Starting AI code review...")
        try:
            review_feedback = review_service.review_pr_diff(pr_diff, pr_files)
            print(f"✅ AI review completed: {review_feedback['overall_assessment']}")
        except Exception as e:
            print(f"❌ AI review failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI review failed: {e}")
        
        # STEP 9: Format feedback as GitHub comments
        inline_comments = github_service.create_inline_comments(review_feedback)
        print(f"💬 Created {len(inline_comments)} inline comments")
        
        # STEP 10: Post review back to GitHub
        try:
            success = github_service.post_pr_review(
                repo_owner=pr_data["repo_owner"],
                repo_name=pr_data["repo_name"],
                pr_number=pr_data["pr_number"],
                comments=inline_comments,
                review_body=review_feedback["summary"]
            )
            
            if success:
                print("✅ Review posted to GitHub successfully!")
                return {
                    "message": "✅ Code review completed and posted",
                    "pr_number": pr_data["pr_number"],
                    "assessment": review_feedback["overall_assessment"],
                    "issues_found": len(review_feedback["issues"])
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to post review")
                
        except Exception as e:
            print(f"❌ Failed to post review: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to post review: {e}")
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OPTIONAL: Manual PR review endpoint (for testing)
# ============================================================================

@app.post("/review/pr")
async def manual_pr_review(pr_url: str):
    """
    Manually trigger a PR review (for testing).
    
    Example: POST /review/pr?pr_url=https://github.com/owner/repo/pull/123
    
    LOGIC: Same as webhook, but you trigger it manually
    Useful for testing without setting up webhooks
    """
    
    # Parse PR URL to extract owner, repo, and PR number
    # Format: https://github.com/owner/repo/pull/123
    try:
        parts = pr_url.rstrip('/').split('/')
        repo_owner = parts[-4]
        repo_name = parts[-3]
        pr_number = int(parts[-1])
    except:
        raise HTTPException(status_code=400, detail="Invalid PR URL format")
    
    print(f"🔍 Manual review triggered for PR #{pr_number}")
    
    # Follow same flow as webhook (steps 6-10)
    try:
        # Fetch diff
        pr_diff = github_service.get_pr_diff(repo_owner, repo_name, pr_number)
        
        # Fetch files
        pr_files = github_service.get_pr_files(repo_owner, repo_name, pr_number)
        
        # AI review
        review_feedback = review_service.review_pr_diff(pr_diff, pr_files)
        
        # Format comments
        inline_comments = github_service.create_inline_comments(review_feedback)
        
        # Post review
        success = github_service.post_pr_review(
            repo_owner, repo_name, pr_number,
            inline_comments, review_feedback["summary"]
        )
        
        if success:
            return {
                "message": "✅ Manual review completed",
                "pr_url": pr_url,
                "assessment": review_feedback["overall_assessment"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to post review")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# APP STARTUP
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )