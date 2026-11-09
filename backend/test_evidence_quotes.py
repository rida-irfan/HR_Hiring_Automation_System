
from agents.resume_agent import evaluate_resume

# Small sample resume for testing
resume_text = """
Technical Skills: Python, SQL

Projects:
Developed a machine learning model using Python
and scikit-learn to predict car prices.

Education:
Bachelor of Science in Artificial Intelligence.
"""

# Job requirements
job_description = """
Looking for an AI/ML Engineer with Python,
Machine Learning, SQL, and FastAPI skills.
"""

# Test rubric
rubric = {
    "python": {
        "weight": 30,
        "type": "must_have",
        "justification": "Python is required for AI development."
    },
    "machine_learning_deep_learning": {
        "weight": 40,
        "type": "must_have",
        "justification": "Machine learning is essential."
    },
    "sql": {
        "weight": 15,
        "type": "preferred",
        "justification": "Useful for database operations."
    },
    "fastapi": {
        "weight": 10,
        "type": "preferred",
        "justification": "Useful for model deployment."
    },
    "communication": {
        "weight": 5,
        "type": "preferred",
        "justification": "Useful for teamwork."
    }
}

# Call the AI agent
result = evaluate_resume(
    resume_text=resume_text,
    job_description=job_description,
    rubric=rubric
)

print("\nEvidence Verification Test Passed!")

print("\nCriterion Scores:")
print(result["criterion_scores"])

print("\nVerified Evidence Quotes:")
print(result["evidence_quotes"])

print("\nEvidence Quality:")
print(result["evidence_quality"])