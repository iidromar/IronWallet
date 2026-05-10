from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from resources.statements.statement_schema import StatementResponse
from resources.statements.statement_service import list_statements

router = APIRouter()


@router.get("", response_model=list[StatementResponse])
def statements(wallet_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return list_statements(db, wallet_id)
