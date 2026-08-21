import logging

import httpx
from fastapi import HTTPException, status

from config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FALLBACK_MODELS = [
    "google/gemma-4-26b-a4b-it:free",
    "cohere/north-mini-code:free",
    "liquid/lfm-2.5-2.6b:free",
]


async def generate_note_summary(text: str) -> str:
    if len(text.strip()) < 50:
        return text

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Secret Notes App",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for model_name in FALLBACK_MODELS:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Сделай краткое саммари текста на языке оригинала. Максимум"
                            " 2-3 предложения. Возвращай ТОЛЬКО текст саммари."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                "max_tokens": 200,
                "temperature": 0.3,
            }

            try:
                response = await client.post(
                    OPENROUTER_URL, headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()

                choices = data.get("choices", [])
                if (
                    choices
                    and "message" in choices[0]
                    and "content" in choices[0]["message"]
                ):
                    summary = choices[0]["message"]["content"].strip()
                    if summary:
                        return summary

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                print(
                    f"--- MODEL {model_name} FAILED, TRYING NEXT ---",
                    flush=True,
                )
                logger.warning(
                    f"Model {model_name} failed with error: {e}. Trying fallback..."
                )
                continue

    logger.error("All LLM fallback models failed")
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Ошибка внешнего AI-сервиса",
    )