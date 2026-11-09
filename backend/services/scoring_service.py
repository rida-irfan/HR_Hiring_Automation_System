
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate project root and load Azure credentials
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def calculate_weighted_score(criterion_scores, rubric):
    """
    Calculate a provisional weighted score.

    Supports:
    1. Old rubric: {"python": 40, "sql": 60}
    2. New rubric: {"python": {
           "weight": 40,
           "type": "must_have",
           "justification": "Core job requirement"
       }, ...}

    Returns a float for compatibility with existing code.
    """

    if not isinstance(rubric, dict) or not rubric:
        raise ValueError("Scoring rubric cannot be empty.")

    if not isinstance(criterion_scores, dict):
        raise ValueError("Criterion scores must be a dictionary.")

    if set(criterion_scores) != set(rubric):
        raise ValueError(
            "AI scores must match the rubric criteria."
        )

    weights = {}

    for criterion, configuration in rubric.items():

        if isinstance(configuration, dict):
            weight = configuration.get("weight")

            if configuration.get("type") not in (
                "must_have", "preferred"
            ):
                raise ValueError(
                    f"Invalid criterion type: {criterion}"
                )

            justification = configuration.get("justification")

            if (
                not isinstance(justification, str)
                or not justification.strip()
            ):
                raise ValueError(
                    f"Missing weight justification: {criterion}"
                )

        else:
            # Support existing numeric rubrics
            weight = configuration

        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not 0 <= weight <= 100
        ):
            raise ValueError(
                f"Invalid weight for criterion: {criterion}"
            )

        weights[criterion] = weight

    if abs(sum(weights.values()) - 100) > 0.001:
        raise ValueError(
            "Rubric weights must total 100."
        )

    weighted_total = 0
    assessed_weight = 0

    for criterion, weight in weights.items():

        score = criterion_scores[criterion]

        if score is None:
            continue

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not 0 <= score <= 100
        ):
            raise ValueError(
                f"Invalid score for criterion: {criterion}"
            )

        weighted_total += score * (weight / 100)
        assessed_weight += weight

    if assessed_weight == 0:
        raise ValueError(
            "No criteria could be scored. Manual review required."
        )

    # This is a provisional score, not a hiring decision.
    return round(weighted_total, 2)


def get_scoring_review_details(criterion_scores, rubric):
    """
    Identify unassessed criteria and calculate evidence coverage.
    """

    missing_criteria = []
    must_have_to_verify = []
    assessed_weight = 0

    for criterion, configuration in rubric.items():

        if isinstance(configuration, dict):
            weight = configuration["weight"]
            criterion_type = configuration["type"]
        else:
            weight = configuration
            criterion_type = "unspecified"

        if criterion_scores[criterion] is None:
            missing_criteria.append(criterion)

            if criterion_type == "must_have":
                must_have_to_verify.append(criterion)
        else:
            assessed_weight += weight

    return {
        "assessed_weight_percentage": round(assessed_weight, 2),
        "unassessed_criteria": missing_criteria,
        "must_have_to_verify": must_have_to_verify,
        "requires_human_review": True
    }
