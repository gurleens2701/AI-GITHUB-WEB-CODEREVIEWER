import openai
from backend.config.settings import settings

# OpenAI API Key - Replace with your own API key
client = openai.OpenAI(api_key=settings.openai_api_key)
