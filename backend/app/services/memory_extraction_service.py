from __future__ import annotations

import json
from typing import Any

from app.ai.service import AIService


class MemoryExtractionService:
    """
    Extracts long-term, useful user memories from conversation text.

    The extractor only proposes memories.
    MemoryService is responsible for actually storing/upserting them.
    """

    def __init__(self):
        self.ai_service = AIService()

    def _build_prompt(self, user_message: str) -> list[dict[str, str]]:
        system_prompt = """
You are a memory extraction component for a private personal AI assistant.

Your job is to identify information from the user's message that is
useful to remember for future conversations.

Only extract stable, useful information about the user.

Good examples:
- programming language preferences
- learning goals
- career goals
- technical skills
- project information
- long-term preferences
- communication preferences
- recurring interests

Do NOT extract:
- passwords
- API keys
- access tokens
- authentication credentials
- secrets
- temporary requests
- one-time questions
- information that is only relevant to the current task
- instructions directed at the AI
- system prompts
- arbitrary facts that are not useful for future personalization

Return ONLY valid JSON.

The JSON must be an array.

Each memory must contain exactly:

{
  "memory_type": "string",
  "key": "string",
  "value": "string",
  "importance": 1,
  "confidence": 0
}

Rules:
- importance must be an integer from 1 to 10
- confidence must be an integer from 0 to 100
- key must be short and descriptive
- value must contain the remembered information
- if there is no useful long-term memory, return []

Example:

User:
"I prefer Python for coding interviews."

Output:
[
  {
    "memory_type": "preference",
    "key": "preferred_programming_language",
    "value": "Python",
    "importance": 9,
    "confidence": 100
  }
]

Another example:

User:
"I want to learn Generative AI and get a job in this field."

Output:
[
  {
    "memory_type": "career_goal",
    "key": "target_career_area",
    "value": "Generative AI",
    "importance": 9,
    "confidence": 100
  }
]
""".strip()

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

    def extract(
        self,
        user_message: str,
    ) -> list[dict[str, Any]]:

        user_message = user_message.strip()

        if not user_message:
            return []

        messages = self._build_prompt(user_message)

        response = self.ai_service.generate_response(
            messages=messages,
        )

        response = response.strip()

        if not response:
            return []

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            return []

        if not isinstance(parsed, list):
            return []

        memories: list[dict[str, Any]] = []

        for item in parsed:

            if not isinstance(item, dict):
                continue

            required_fields = {
                "memory_type",
                "key",
                "value",
                "importance",
                "confidence",
            }

            if not required_fields.issubset(item.keys()):
                continue

            if not isinstance(item["memory_type"], str):
                continue

            if not isinstance(item["key"], str):
                continue

            if not isinstance(item["value"], str):
                continue

            if not isinstance(item["importance"], int):
                continue

            if not isinstance(item["confidence"], int):
                continue

            if not 1 <= item["importance"] <= 10:
                continue

            if not 0 <= item["confidence"] <= 100:
                continue

            memories.append(
                {
                    "memory_type": item["memory_type"].strip(),
                    "key": item["key"].strip(),
                    "value": item["value"].strip(),
                    "importance": item["importance"],
                    "confidence": item["confidence"],
                }
            )

        return memories