
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")


async def get_signed_conversation_url():
    if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
        raise RuntimeError(
            "ElevenLabs API key or Agent ID is missing"
        )

    url = (
        "https://api.elevenlabs.io/v1/convai/conversation/"
        "get-signed-url"
    )

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            url,
            params={"agent_id": ELEVENLABS_AGENT_ID},
            headers={
                "xi-api-key": ELEVENLABS_API_KEY
            }
        )

        response.raise_for_status()
        return response.json()["signed_url"]
