import os
from dotenv import load_dotenv

# Locate the project root and load .env
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def calculate_weighted_score(criterion_scores, rubric):
    if not rubric:
        raise ValueError("Scoring rubric cannot be empty.")

    if any(
        not isinstance(weight, (int, float))
        or isinstance(weight, bool)
        or weight < 0
        for weight in rubric.values()
    ):
        raise ValueError("Rubric weights must be non-negative numbers.")

    if abs(sum(rubric.values()) - 100) > 0.001:
        raise ValueError("Rubric weights must total 100.")

    if set(criterion_scores) != set(rubric):
        raise ValueError("AI scores must match the rubric criteria.")

    total_score = 0

    for criterion, weight in rubric.items():
        score = criterion_scores[criterion]
        if score is None:
         continue    

        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= score <= 100
        ):
            raise ValueError(
                f"Invalid score for criterion: {criterion}"
            )

        total_score += score * (weight / 100)

    return round(total_score, 2)


