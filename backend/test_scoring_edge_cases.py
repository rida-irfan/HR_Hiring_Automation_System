
from services.scoring_service import (
    calculate_weighted_score,
    get_scoring_review_details
)

# Sample job rubric
rubric = {
    "python": {
        "weight": 40,
        "type": "must_have",
        "justification": "Python is essential."
    },
    "machine_learning": {
        "weight": 40,
        "type": "must_have",
        "justification": "ML is essential."
    },
    "sql": {
        "weight": 20,
        "type": "preferred",
        "justification": "SQL is useful."
    }
}

# Test Case 1: All skills assessed
scores_1 = {
    "python": 90,
    "machine_learning": 80,
    "sql": 70
}

total_1 = calculate_weighted_score(scores_1, rubric)
details_1 = get_scoring_review_details(scores_1, rubric)

assert total_1 == 82
assert details_1["assessed_weight_percentage"] == 100

print("Test 1 PASSED: All skills assessed.")


# Test Case 2: Preferred skill unassessed
scores_2 = {
    "python": 90,
    "machine_learning": 80,
    "sql": None
}

total_2 = calculate_weighted_score(scores_2, rubric)
details_2 = get_scoring_review_details(scores_2, rubric)

assert total_2 == 68
assert details_2["assessed_weight_percentage"] == 80
assert "sql" in details_2["unassessed_criteria"]

print("Test 2 PASSED: Missing preferred skill handled.")


# Test Case 3: Must-have skill unassessed
scores_3 = {
    "python": 90,
    "machine_learning": None,
    "sql": 70
}

details_3 = get_scoring_review_details(scores_3, rubric)

assert "machine_learning" in details_3["must_have_to_verify"]
assert details_3["requires_human_review"] is True

print("Test 3 PASSED: Missing must-have requires HR review.")

print("\nAll scoring edge-case tests passed!")
