from database import SessionLocal
from models import Candidate
from services.resume_parser import extract_resume_text


db = SessionLocal()

try:
    # Get our previously registered candidate
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == 1
    ).first()

    if not candidate or not candidate.resume_path:
        print("Candidate or resume not found.")

    else:
        # Extract resume text
        resume_text = extract_resume_text(
            candidate.resume_path
        )

        print("Resume extraction successful!")
        print("\nExtracted text:\n")
        print(resume_text[:1000])

finally:
    db.close()