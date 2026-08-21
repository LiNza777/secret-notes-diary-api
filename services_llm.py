import asyncio
import logging

import httpx
from fastapi import HTTPException, status

from config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def generate_note_summary(text: str) -> str:
    if len(text.strip()) < 50:
        return text

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Secret Notes App",
    }

    payload = {
        "model": "google/gemma-4-26b-a4b-it:free",
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

    max_retries = 2
    data = None

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(
                    OPENROUTER_URL, headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()
                break
            except httpx.HTTPStatusError as e:
                if attempt == max_retries:
                    print(
                        f"--- OPENROUTER ERROR STATUS: {e.response.status_code} ---",
                        flush=True,
                    )
                    print(
                        f"--- OPENROUTER ERROR BODY: {e.response.text} ---", flush=True
                    )

                    logger.error(f"LLM API Error: {e.response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Ошибка внешнего AI-сервиса",
                    ) from e

                logger.warning(f"LLM API attempt {attempt} failed, retrying...")
                await asyncio.sleep(1.0)

            except httpx.RequestError as e:
                if attempt == max_retries:
                    print(f"--- OPENROUTER NETWORK ERROR: {e} ---", flush=True)

                    logger.error(f"LLM Network Error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail="AI-сервис недоступен",
                    ) from e

                logger.warning(f"LLM Network attempt {attempt} failed, retrying...")
                await asyncio.sleep(1.0)

    choices = data.get("choices", []) if data else []
    if (
        not choices
        or "message" not in choices[0]
        or "content" not in choices[0]["message"]
    ):
        logger.error("LLM API returned no summary content")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ошибка внешнего AI-сервиса",
        )

    summary = choices[0]["message"]["content"].strip()
    return summary or text
