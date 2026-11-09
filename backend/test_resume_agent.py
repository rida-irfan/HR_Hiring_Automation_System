
from database import SessionLocal
from models import Candidate, Requisition, ResumeEvaluation
from services.resume_parser import extract_resume_text
from agents.resume_agent import evaluate_resume
from services.scoring_service import (
    calculate_weighted_score,
    get_scoring_review_details
)


# Create database session
db = SessionLocal()

try:
    # Step 1: Fetch candidate and job requisition
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == 1
    ).first()

    requisition = db.query(Requisition).filter(
        Requisition.requisition_id == 5
    ).first()

    # Step 2: Validate candidate and requisition
    if not candidate or not candidate.resume_path:
        print("Candidate or resume not found.")

    elif not requisition:
        print("Job requisition not found.")

    elif requisition.status != "Approved":
        raise ValueError(
            "Resume evaluation blocked: requisition must be approved by HR."
        )

    elif not requisition.rubric:
        print("Job scoring rubric not found.")

    else:
        # Step 3: Extract resume text and parsing warnings
        resume_text, parsing_warnings = extract_resume_text(
            candidate.resume_path
        )

        print("\nResume extraction completed.")
        print("Parsing warnings:", parsing_warnings)

        # Step 4: Stop scoring if extraction is incomplete
        if parsing_warnings or not resume_text.strip():
            print("\nResume requires manual review.")

            raise ValueError(
                "AI scoring stopped because resume extraction "
                "may be incomplete. Manual review is required."
            )

        # Step 5: Evaluate resume using Azure GPT-4.1 mini
        result = evaluate_resume(
            resume_text=resume_text,
            job_description=requisition.job_description,
            rubric=requisition.rubric
        )

        print("\nAI Evaluation Result:")
        print(result)

        print("\nVerified Evidence Quotes:")
        print(result["evidence_quotes"])

        print("\nEvidence Quality:")
        print(result["evidence_quality"])

        # Step 6: Calculate weighted score
        final_score = calculate_weighted_score(
            result["criterion_scores"],
            requisition.rubric
        )

        # Step 6.1: Get scoring review details
        review_details = get_scoring_review_details(
            result["criterion_scores"],
            requisition.rubric
        )

        print("\nScoring Review Details:", review_details)
        print("\nFinal Weighted Score:", final_score)

        # Step 7: Save evaluation in SQLite
        evaluation = ResumeEvaluation(
            candidate_id=candidate.candidate_id,
            requisition_id=requisition.requisition_id,
            total_score=final_score,
            criterion_scores=result["criterion_scores"],
            scoring_review_details=review_details,
            evidence=result["evidence"],
            structured_evidence=result["structured_evidence"],
            evidence_quotes=result["evidence_quotes"],
            evidence_quality=result["evidence_quality"],
            missing_or_unclear_items=result[
                "missing_or_unclear_items"
            ],
            parsing_warnings=parsing_warnings,
            warnings=result["warnings"],
            recommendation_for_human_review=result[
                "recommendation_for_human_review"
            ],
            model_version="gpt-4.1-mini",
            review_status="Pending HR Review"
        )

        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        # Step 8: Display saved evaluation information
        print("\nEvaluation saved successfully!")
        print("Evaluation ID:", evaluation.evaluation_id)
        print("Candidate ID:", evaluation.candidate_id)
        print("Requisition ID:", evaluation.requisition_id)
        print("Overall Score:", evaluation.total_score)
        print("HR Review Status:", evaluation.review_status)

except Exception as error:
    db.rollback()
    print("\nError:", error)
    raise

finally:
    # Always close database connection
    db.close()
