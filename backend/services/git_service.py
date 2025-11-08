import hmac
import hashlib
import requests
from typing import Dict, Any, List, Optional
from backend.config.settings import settings


class GitHubService:
    """Service for interacting with GitHub API and webhooks."""
    
    def __init__(self):
        self.github_token = settings.github_token
        self.webhook_secret = settings.github_webhook_secret
        self.base_url = "https://api.github.com"
    
    
    def verify_webhook_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify webhook came from GitHub.
        
        LOGIC: Like verifying a push notification signature in mobile apps.
        """
        if not signature_header:
            raise ValueError("❌ Missing signature header")
        
        try:
            algorithm, github_signature = signature_header.split("=")
        except ValueError:
            raise ValueError("❌ Invalid signature format")
        
        # Create expected signature
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        # Secure comparison
        if not hmac.compare_digest(github_signature, expected_signature):
            raise ValueError("❌ Signature verification failed!")
        
        return True
    
    
    def parse_webhook_pr(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract PR information from webhook payload.
        
        LOGIC: Like parsing JSON from an API response in mobile dev.
        Extract: repo owner, repo name, PR number, action type
        """
        try:
            pr_data = {
                "action": payload.get("action"),  # "opened", "synchronize", etc.
                "pr_number": payload["pull_request"]["number"],
                "repo_owner": payload["repository"]["owner"]["login"],
                "repo_name": payload["repository"]["name"],
                "pr_url": payload["pull_request"]["html_url"],
            }
            return pr_data
        except KeyError as e:
            print(f"❌ Failed to parse webhook payload: {e}")
            return None
    
    
    def get_pr_diff(self, repo_owner: str, repo_name: str, pr_number: int) -> str:
        """
        Fetch the code diff from GitHub for a PR.
        
        LOGIC: Make API call to GitHub to get "what changed in this PR"
        Similar to: Fetching data from REST API in mobile app
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3.diff"  # Request diff format
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text  # The actual diff content
        else:
            raise Exception(f"❌ Failed to fetch PR diff: {response.status_code}")
    
    
    def get_pr_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get list of files changed in the PR.
        
        LOGIC: Get metadata about what files were modified
        Returns: List of file objects with filename, status, changes, etc.
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()  # List of file objects
        else:
            raise Exception(f"❌ Failed to fetch PR files: {response.status_code}")
    
    
    def create_inline_comments(self, review_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format AI feedback into GitHub inline comments.
        
        LOGIC: Convert AI's response into the format GitHub expects
        Like formatting data before sending to an API in mobile dev
        
        GitHub expects:
        {
            "path": "filename.py",
            "line": 10,
            "body": "Consider using a try-except here"
        }
        """
        comments = []
        
        # This will depend on how your AI structures its feedback
        # For now, basic structure:
        if "issues" in review_feedback:
            for issue in review_feedback["issues"]:
                comment = {
                    "path": issue.get("file"),
                    "line": issue.get("line"),
                    "body": issue.get("message")
                }
                comments.append(comment)
        
        return comments
    
    
    def post_pr_review(
        self, 
        repo_owner: str, 
        repo_name: str, 
        pr_number: int, 
        comments: List[Dict[str, Any]], 
        review_body: str
    ) -> bool:
        """
        Post the AI review back to GitHub PR.
        
        LOGIC: Send formatted comments back to GitHub
        Like posting data to an API endpoint in mobile dev
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # GitHub review format
        review_data = {
            "body": review_body,
            "event": "COMMENT",  # Can be: COMMENT, APPROVE, REQUEST_CHANGES
            "comments": comments
        }
        
        response = requests.post(url, json=review_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Review posted successfully!")
            return True
        else:
            print(f"❌ Failed to post review: {response.status_code} - {response.text}")
            return False


# Create singleton instance
github_service = GitHubService()