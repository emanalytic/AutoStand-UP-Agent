from .base_provider import BaseLLMProvider
from groq import Groq
import time
from typing import List, Dict


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation."""
    
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = Groq(api_key=api_key)
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate a chat completion using Groq API."""
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise Exception(f"Groq API failed after {retry_attempts} attempts: {str(e)}")