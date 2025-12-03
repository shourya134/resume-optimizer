"""
Claude API Client Wrapper

Provides a clean interface for interacting with the Anthropic Claude API.
Handles authentication, request formatting, and error handling.
"""

import os
from typing import Optional, Dict, Any, List
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class ClaudeClient:
    """Wrapper for Anthropic Claude API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        """
        Initialize the Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (defaults to CLAUDE_MODEL env var or claude-sonnet-4-5)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a response from Claude.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to guide behavior
            max_tokens: Override default max_tokens
            temperature: Override default temperature

        Returns:
            The generated text response

        Raises:
            Exception: If API call fails
        """
        try:
            message_params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                message_params["system"] = system_prompt

            response = self.client.messages.create(**message_params)

            # Extract text from response
            return response.content[0].text

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        expected_format: str = "json",
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured response (JSON) from Claude.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            expected_format: Expected format (currently only "json")
            max_tokens: Override default max_tokens

        Returns:
            Parsed JSON response as dictionary

        Raises:
            Exception: If API call fails or response is not valid JSON
        """
        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nPlease respond with valid JSON only, no additional text."

        response_text = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for structured output
        )

        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")

    def extract_keywords(
        self,
        text: str,
        context: Optional[str] = None,
        max_keywords: int = 20,
    ) -> List[str]:
        """
        Extract important keywords from text using Claude.

        Args:
            text: The text to analyze
            context: Optional context (e.g., "resume" or "job description")
            max_keywords: Maximum number of keywords to extract

        Returns:
            List of extracted keywords
        """
        prompt = f"""Extract the {max_keywords} most important keywords and key phrases from the following {context or 'text'}.
Focus on:
- Technical skills and tools
- Industry-specific terms
- Action verbs and competencies
- Qualifications and certifications

Text:
{text}

Return only a JSON array of keywords, like: ["keyword1", "keyword2", ...]"""

        try:
            result = self.generate_structured(prompt)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "keywords" in result:
                return result["keywords"]
            else:
                return []
        except Exception as e:
            print(f"Warning: Keyword extraction failed: {e}")
            return []

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
        context: Optional[str] = None,
    ) -> float:
        """
        Calculate semantic similarity between two texts using Claude.

        Args:
            text1: First text (e.g., resume)
            text2: Second text (e.g., job description)
            context: Optional context for the comparison

        Returns:
            Similarity score from 0 to 100
        """
        prompt = f"""Calculate the semantic similarity between these two texts{' for ' + context if context else ''}.

Text 1:
{text1}

Text 2:
{text2}

Analyze how well Text 1 matches the requirements, skills, and keywords in Text 2.
Return a JSON object with:
- "score": A number from 0-100 indicating similarity
- "reasoning": Brief explanation of the score

Example: {{"score": 75, "reasoning": "Strong match on technical skills, missing some required experience"}}"""

        try:
            result = self.generate_structured(prompt, max_tokens=1000)
            return float(result.get("score", 0))
        except Exception as e:
            print(f"Warning: Similarity calculation failed: {e}")
            return 0.0


# Singleton instance for easy import
_default_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """
    Get or create the default Claude client instance.

    Returns:
        Singleton ClaudeClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = ClaudeClient()
    return _default_client
