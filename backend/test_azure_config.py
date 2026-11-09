from services.scoring_service import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT
)

print("Endpoint loaded:", bool(AZURE_OPENAI_ENDPOINT))
print("API key loaded:", bool(AZURE_OPENAI_API_KEY))
print("Deployment loaded:", bool(AZURE_OPENAI_DEPLOYMENT))