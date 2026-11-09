
from openai import OpenAI

from services.scoring_service import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT
)

# Connect to the Azure OpenAI v1 endpoint
client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT.rstrip("/") + "/",
    api_key=AZURE_OPENAI_API_KEY
)

# Send a test message
response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {
            "role": "user",
            "content": "Reply with: HR Hiring Agent is ready!"
        }
    ],
    max_tokens=50
)

print(response.choices[0].message.content)
