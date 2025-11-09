# 🤖 AI Code Generator & Review System

An intelligent code generation and automated code review system powered by OpenAI and integrated with GitHub webhooks.

## ✨ Features

### Code Generator
- 🚀 Generate code in multiple programming languages (Python, JavaScript, Java, C++, Go, etc.)
- 🧪 Automatically generate unit tests for your code
- 📚 Generate comprehensive documentation with docstrings
- 💾 Save generated code to files
- 📋 Copy code to clipboard

### AI Code Review (GitHub Integration)
- 🔍 Automatically reviews Pull Requests when opened or updated
- 🛡️ Detects security vulnerabilities (SQL injection, hardcoded secrets, etc.)
- 🐛 Identifies bugs and logic errors
- ⚡ Suggests performance improvements
- 📖 Checks for best practices and code style
- 💬 Posts detailed inline comments on GitHub PRs

## 🏗️ Architecture
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   GitHub    │────────▶│  Your Server │────────▶│   OpenAI    │
│  (Webhook)  │         │   (FastAPI)  │         │     API     │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Gradio UI  │
                        │  (Frontend)  │
                        └──────────────┘
```

## 📦 Project Structure
```
aicodeservice/
├── backend/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── services/
│   │   ├── aicode_service.py    # Code generation logic
│   │   ├── file_handler.py      # File operations
│   │   ├── git_service.py       # GitHub API integration
│   │   ├── review_service.py    # AI code review logic
│   │   └── openai_client.py     # OpenAI client setup
│   └── app.py                    # FastAPI application (main backend)
├── frontend/
│   ├── components/
│   │   └── ui_components.py     # Gradio UI components
│   ├── static/
│   │   └── styles.css           # Custom CSS styling
│   └── app.py                    # Gradio frontend application
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── start_services.py            # Script to start both services
└── README.md                     # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- GitHub account
- (Optional) GitHub Personal Access Token for webhook integration

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-code-review-system.git
cd ai-code-review-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Required for Code Generation
OPENAI_API_KEY=your_openai_api_key_here

# Backend Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=7819

# OpenAI Model Settings
MODEL_NAME=gpt-4
TEMPERATURE=0.3

# Required for GitHub Webhook Integration (Optional)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### 4. Run the Application
