from pydantic import BaseModel, ConfigDict
from typing import Optional


# Requisition schemas
class RequisitionCreate(BaseModel):
    title: str
    job_description: str
    rubric: Optional[dict] = None
    created_by: Optional[str] = None


class RequisitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    requisition_id: int
    title: str
    job_description: str
    rubric: Optional[dict] = None
    status: str
    created_by: Optional[str] = None


# Candidate schemas
class CandidateCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_path: Optional[str] = None
    consent_preferences: Optional[dict] = None

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    candidate_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_path: Optional[str] = None
    consent_preferences: Optional[dict] = None
    current_status: str

class ResumeEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    review_status: str
    evaluation_id: int
    candidate_id: int
    requisition_id: int
    total_score: float
    criterion_scores: dict
    evidence: dict
    warnings: list
    model_version: Optional[str] = None

from typing import Literal

class EvaluationReviewRequest(BaseModel):
    review_status: Literal[
        "Approved for Screening",
        "Needs Manual Review"
    ]

