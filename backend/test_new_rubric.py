
from services.scoring_service import (
    calculate_weighted_score,
    get_scoring_review_details
)

# New configurable rubric
rubric = {
    "python": {
        "weight": 30,
        "type": "must_have",
        "justification": "Python is essential for AI/ML development."
    },
    "machine_learning_deep_learning": {
        "weight": 40,
        "type": "must_have",
        "justification": "Core requirement for building AI models."
    },
    "sql": {
        "weight": 15,
        "type": "preferred",
        "justification": "Useful for working with databases."
    },
    "fastapi": {
        "weight": 10,
        "type": "preferred",
        "justification": "Useful for deploying ML models."
    },
    "communication": {
        "weight": 5,
        "type": "preferred",
        "justification": "Useful for teamwork."
    }
}

# Example AI scores
criterion_scores = {
    "python": 85,
    "machine_learning_deep_learning": None,
    "sql": 70,
    "fastapi": None,
    "communication": 60
}

# Calculate provisional score
score = calculate_weighted_score(
    criterion_scores,
    rubric
)

# Identify criteria requiring HR verification
review_details = get_scoring_review_details(
    criterion_scores,
    rubric
)

print("Provisional Weighted Score:", score)
print("Review Details:", review_details)
