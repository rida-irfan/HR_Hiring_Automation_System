
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Literal
from datetime import datetime


# Requisition rubric configuration
class RubricCriterion(BaseModel):
    weight: float = Field(gt=0, le=100)
    type: Literal["must_have", "preferred"]
    justification: str = Field(min_length=1)


class RequisitionCreate(BaseModel):
    title: str
    job_description: str
    rubric: dict[str, RubricCriterion]
    created_by: Optional[str] = None

    @model_validator(mode="after")
    def validate_rubric(self):
        if not self.rubric:
            raise ValueError("Rubric cannot be empty.")

        total_weight = sum(
            criterion.weight
            for criterion in self.rubric.values()
        )

        if abs(total_weight - 100) > 0.000001:
            raise ValueError(
                "Rubric weights must add up to 100."
            )

        return self


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


# Resume evaluation response

# Resume evaluation response
class ResumeEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evaluation_id: int
    candidate_id: int
    requisition_id: int

    total_score: float
    overall_score: float

    criterion_scores: dict
    evidence: dict
    structured_evidence: Optional[dict] = None
    evidence_quotes: Optional[dict] = None
    evidence_quality: Optional[dict] = None
    scoring_review_details: Optional[dict] = None
    warnings: list

    missing_or_unclear_items: Optional[list] = None
    parsing_warnings: Optional[list] = None
    recommendation_for_human_review: Optional[str] = None

    model_version: Optional[str] = None
    created_at: datetime
    review_status: str

    @model_validator(mode="before")
    @classmethod
    def add_overall_score(cls, data):
        # Handle SQLAlchemy database objects
        if not isinstance(data, dict):
            return {
                field: getattr(data, field, None)
                for field in cls.model_fields
                if field != "overall_score"
            } | {
                "overall_score": data.total_score
            }

        # Handle dictionary responses
        data = data.copy()
        data["overall_score"] = data.get(
            "overall_score",
            data.get("total_score")
        )

        return data


# HR review request
class EvaluationReviewRequest(BaseModel):
    review_status: Literal[
        "Approved for Screening",
        "Needs Manual Review"
    ]
