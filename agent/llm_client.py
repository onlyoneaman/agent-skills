"""Simple OpenAI client for agent skills"""

import os
from typing import List, Dict, Optional
from openai import OpenAI


class LLMClient:
    """Simple OpenAI client wrapper"""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None
    ) -> Dict:
        """Send chat request to OpenAI"""

        kwargs = {
            "model": self.model,
            "messages": messages
        }

        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        # Convert to simple format
        result = {
            "content": message.content or "",
            "tool_calls": []
        }

        if message.tool_calls:
            for tc in message.tool_calls:
                result["tool_calls"].append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

        return result
