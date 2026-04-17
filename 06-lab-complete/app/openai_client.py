from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.chat_service import LLMReply, ProviderUnavailableError


@dataclass
class OpenAIClient:
    api_key: str
    model: str
    timeout_seconds: float
    base_url: str = "https://api.openai.com/v1"

    def __call__(self, question: str, history: list[dict]) -> LLMReply:
        input_messages = self._build_input_messages(question, history)
        url = f"{self.base_url.rstrip('/')}/responses"

        try:
            response = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": input_messages,
                    "store": False,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("OpenAI request failed") from exc

        data = response.json()
        text = self._extract_text(data)
        if not text:
            raise ProviderUnavailableError("OpenAI returned an empty response")

        usage = data.get("usage", {})
        return LLMReply(
            text=text,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )

    @staticmethod
    def _build_input_messages(question: str, history: list[dict]) -> list[dict[str, str]]:
        messages = []
        for item in history:
            role = item.get("role", "user")
            if role not in {"user", "assistant", "developer", "system"}:
                role = "user"
            content = str(item.get("content", "")).strip()
            if content:
                messages.append({"role": role, "content": content})

        if not messages:
            messages.append({"role": "user", "content": question})
        return messages

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        parts = []
        for output_item in data.get("output", []):
            for content_item in output_item.get("content", []):
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text)
        return "".join(parts).strip()


def build_llm(settings):
    if settings.llm_provider == "openai":
        return OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            timeout_seconds=settings.openai_timeout_seconds,
            base_url=settings.openai_api_base_url,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
