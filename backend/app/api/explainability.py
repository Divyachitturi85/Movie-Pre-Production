from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.explainability import AIExplainabilityRecord
from app.schemas.explainability import ExplainabilityResponse

router = APIRouter(prefix="/projects/{project_id}/explainability", tags=["AI Explainability"])

@router.get("", response_model=List[ExplainabilityResponse])
def get_explainability_records(
    project_id: int,
    stage: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns transparency audit trail for academic demonstration.
    Reports input data, AI technique/model, detected entity, confidence score,
    and whether fallback was activated.
    """
    query = db.query(AIExplainabilityRecord).filter(AIExplainabilityRecord.project_id == project_id)
    if stage:
        query = query.filter(AIExplainabilityRecord.stage == stage)
    return query.order_by(AIExplainabilityRecord.created_at.asc()).all()
