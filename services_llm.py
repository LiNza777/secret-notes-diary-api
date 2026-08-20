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
  }

  payload = {
      "model": "google/gemini-2.0-flash-lite-001",
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

  async with httpx.AsyncClient(timeout=10.0) as client:
    try:
      response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
      response.raise_for_status()
      data = response.json()
      return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
      logger.error(f"LLM API Error: {e.response.text}")
      raise HTTPException(
          status_code=status.HTTP_502_BAD_GATEWAY,
          detail="Ошибка внешнего AI-сервиса",
      )
    except httpx.RequestError as e:
      logger.error(f"LLM Network Error: {e}")
      raise HTTPException(
          status_code=status.HTTP_504_GATEWAY_TIMEOUT,
          detail="AI-сервис недоступен",
      )