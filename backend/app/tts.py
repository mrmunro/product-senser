from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


async def synthesize_elevenlabs(text: str, voice_id: Optional[str] = None) -> bytes:
    """Synthesize speech audio (MP3) via ElevenLabs REST API."""
    if not settings.elevenlabs_configured:
        raise ValueError("ELEVENLABS_API_KEY is not configured in .env")

    target_voice = (voice_id or settings.elevenlabs_voice_id).strip()
    url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{target_voice}"

    headers = {
        "xi-api-key": settings.elevenlabs_api_key.strip(),
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": settings.elevenlabs_model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            url,
            params={"output_format": "mp3_44100_128"},
            headers=headers,
            json=payload,
        )

    if response.status_code >= 400:
        detail = response.text[:300]
        logger.error("ElevenLabs TTS failed (%s): %s", response.status_code, detail)
        raise RuntimeError(f"ElevenLabs API error ({response.status_code}): {detail}")

    return response.content
