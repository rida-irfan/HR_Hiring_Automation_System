
from database import SessionLocal
from models import Candidate, Requisition, ResumeEvaluation
from services.resume_parser import extract_resume_text
from agents.resume_agent import evaluate_resume
from services.scoring_service import calculate_weighted_score

db = SessionLocal()

try:
    # Fetch candidate and job requisition
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == 1
    ).first()

    requisition = db.query(Requisition).filter(
        Requisition.requisition_id == 1
    ).first()

    if not candidate or not candidate.resume_path:
        print("Candidate or resume not found.")

    elif not requisition:
        print("Job requisition not found.")

    elif not requisition.rubric:
        print("Job scoring rubric not found.")

    else:
        # Extract complete resume text
        resume_text = extract_resume_text(
            candidate.resume_path
        )

        # Evaluate resume using GPT-4.1 mini
        result = evaluate_resume(
            resume_text=resume_text,
            job_description=requisition.job_description,
            rubric=requisition.rubric
        )

        print("\nAI Evaluation Result:")
        print(result)

        # Calculate weighted score
        final_score = calculate_weighted_score(
            result["criterion_scores"],
            requisition.rubric
        )

        print("\nFinal Weighted Score:", final_score)

        # Save evaluation in SQLite
        evaluation = ResumeEvaluation(
            candidate_id=candidate.candidate_id,
            requisition_id=requisition.requisition_id,
            total_score=final_score,
            criterion_scores=result["criterion_scores"],
            evidence=result["evidence"],
            warnings=result["warnings"],
            model_version="gpt-4.1-mini"
        )

        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        print("\nEvaluation saved successfully!")
        print("Evaluation ID:", evaluation.evaluation_id)

finally:
    db.close()
