from typing import Dict, Any, List
from backend.services.openai_client import client
from backend.config.settings import settings


class ReviewService:
    """Service for AI-powered code review."""
    
    def __init__(self):
        self.model = settings.model_name
        self.temperature = 0.3  # Lower = more focused, deterministic
    
    
    def review_pr_diff(self, diff: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main review function - analyzes PR diff and returns feedback.
        
        LOGIC:
        1. Take the code diff (what changed)
        2. Send to AI with specific review instructions
        3. Parse AI's response
        4. Return structured feedback
        
        Args:
            diff: The git diff showing code changes
            files: List of files changed (metadata)
            
        Returns:
            Dictionary with review feedback
        """
        
        # Check if we should use real AI or mock (for testing)
        if not settings.openai_api_key:
            print("⚠️  No OpenAI API key - using mock review")
            return self._mock_review_diff(diff, files)
        
        try:
            # Use real AI review
            return self._ai_review_diff(diff, files)
        except Exception as e:
            print(f"❌ AI review failed: {e}")
            # Fallback to mock for safety
            return self._mock_review_diff(diff, files)
    
    
    def _ai_review_diff(self, diff: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use OpenAI to review the code diff.
        
        LOGIC: Similar to your generate_code() but with different prompt.
        Instead of "create code", we ask "find issues in this code".
        """
        
        # Build the prompt for AI
        prompt = self._build_review_prompt(diff, files)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert code reviewer. Analyze code changes and identify:
                    1. Bugs and logic errors
                    2. Security vulnerabilities
                    3. Performance issues
                    4. Best practice violations
                    5. Code style issues
                    
                    Provide specific, actionable feedback with line numbers when possible.
                    Be constructive and helpful in your tone."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=self.temperature
        )
        
        # Extract AI's response
        review_text = response.choices[0].message.content.strip()
        
        # Parse the response into structured format
        return self._parse_ai_response(review_text, files)
    
    
    def _build_review_prompt(self, diff: str, files: List[Dict[str, Any]]) -> str:
        """
        Build the prompt for AI review.
        
        LOGIC: Create clear instructions for the AI
        Include the diff and context about files changed
        """
        
        # Get file names
        file_names = [f["filename"] for f in files]
        
        prompt = f"""
Please review the following code changes from a Pull Request.

**Files Changed:**
{', '.join(file_names)}

**Code Diff:**
```
{diff[:4000]}  # Limit to first 4000 chars to stay within token limits
```

**Review Focus:**
- Identify any bugs or logic errors
- Check for security vulnerabilities (SQL injection, XSS, etc.)
- Note any performance concerns
- Suggest improvements for readability/maintainability
- Check adherence to best practices

Please provide your feedback in a clear, structured format with:
- Specific line numbers or file names when possible
- Severity level (Critical/Major/Minor)
- Actionable suggestions for improvement
"""
        
        return prompt
    
    
    def _parse_ai_response(self, review_text: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse AI's text response into structured format.
        
        LOGIC: Convert free-form text into structured data
        that GitHub API can use for inline comments.
        
        This is a simplified version - you can make it more sophisticated
        by asking AI to return JSON format.
        """
        
        # For now, return a simple structure
        # In production, you'd parse more carefully to extract line numbers
        
        return {
            "summary": review_text,
            "issues": self._extract_issues(review_text, files),
            "overall_assessment": self._get_overall_assessment(review_text)
        }
    
    
    def _extract_issues(self, review_text: str, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract individual issues from AI's review.
        
        LOGIC: Parse the text to find specific issues
        In a real implementation, you'd use regex or ask AI for JSON
        """
        
        issues = []
        
        # Simple parsing - look for lines mentioning file names
        # This is basic - you can improve it!
        lines = review_text.split('\n')
        
        for line in lines:
            # Example: if AI mentions a file and "line X"
            for file_info in files:
                filename = file_info["filename"]
                if filename in line.lower():
                    # Found an issue related to this file
                    issue = {
                        "file": filename,
                        "line": 1,  # Default to line 1 (improve with regex)
                        "message": line.strip(),
                        "severity": self._detect_severity(line)
                    }
                    issues.append(issue)
                    break
        
        # If no specific issues found, create a general comment
        if not issues and files:
            issues.append({
                "file": files[0]["filename"],
                "line": 1,
                "message": review_text[:200] + "...",  # First 200 chars
                "severity": "info"
            })
        
        return issues
    
    
    def _detect_severity(self, text: str) -> str:
        """
        Detect severity level from text.
        
        LOGIC: Look for keywords indicating severity
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'security', 'vulnerable', 'exploit']):
            return 'critical'
        elif any(word in text_lower for word in ['major', 'bug', 'error', 'broken']):
            return 'major'
        elif any(word in text_lower for word in ['minor', 'style', 'formatting', 'suggestion']):
            return 'minor'
        else:
            return 'info'
    
    
    def _get_overall_assessment(self, review_text: str) -> str:
        """
        Determine overall assessment of the PR.
        
        LOGIC: Based on what AI found, is this PR good or needs work?
        """
        text_lower = review_text.lower()
        
        critical_issues = ['critical', 'security', 'vulnerable', 'broken']
        if any(word in text_lower for word in critical_issues):
            return "❌ Changes need attention - critical issues found"
        
        major_issues = ['major', 'bug', 'error']
        if any(word in text_lower for word in major_issues):
            return "⚠️ Good start, but some issues need fixing"
        
        if 'looks good' in text_lower or 'lgtm' in text_lower:
            return "✅ Changes look good!"
        
        return "💬 Review completed - see comments for details"
    
    
    def _mock_review_diff(self, diff: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mock review for testing without OpenAI API.
        
        LOGIC: When you don't have API key yet, return fake data
        so you can test the rest of the system.
        """
        
        print("🤖 Using mock review (no API key)")
        
        # Create fake review data
        mock_issues = []
        for file_info in files[:2]:  # Review first 2 files
            mock_issues.append({
                "file": file_info["filename"],
                "line": 1,
                "message": f"✅ Mock review: {file_info['filename']} looks good! (This is a test comment)",
                "severity": "info"
            })
        
        return {
            "summary": "🤖 This is a MOCK review for testing. Enable OpenAI API for real reviews.\n\nThe code changes look reasonable in this test review.",
            "issues": mock_issues,
            "overall_assessment": "💬 Mock review completed (testing mode)"
        }


# Create singleton instance
review_service = ReviewService()