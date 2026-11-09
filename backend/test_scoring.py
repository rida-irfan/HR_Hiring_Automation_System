from services.scoring_service import calculate_weighted_score

rubric = {
    "python": 30,
    "fastapi": 25,
    "sql": 20,
    "projects": 15,
    "problem_solving": 10
}

criterion_scores = {
    "python": 90,
    "fastapi": 80,
    "sql": 70,
    "projects": 85,
    "problem_solving": 75
}

result = calculate_weighted_score(criterion_scores, rubric)

print("Final Weighted Score:", result)
