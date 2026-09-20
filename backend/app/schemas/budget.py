from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BudgetItemResponse(BaseModel):
    id: int
    category: str
    department: str
    account_code: Optional[str] = None
    description: str
    quantity: float
    unit: str
    unit_rate: float
    days_count: float
    subtotal: float
    is_custom: int
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class BudgetItemUpdate(BaseModel):
    id: Optional[int] = None
    category: Optional[str] = None
    department: Optional[str] = None
    account_code: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_rate: Optional[float] = None
    days_count: Optional[float] = None
    notes: Optional[str] = None

class BudgetResponse(BaseModel):
    id: int
    project_id: int
    currency: str
    subtotal: float
    contingency_rate: float
    contingency_amount: float
    tax_rate: float
    tax_amount: float
    grand_total: float
    status: str
    disclaimer: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[BudgetItemResponse]] = []

    model_config = ConfigDict(from_attributes=True)

class BudgetConfigUpdate(BaseModel):
    contingency_rate: Optional[float] = None
    tax_rate: Optional[float] = None
    currency: Optional[str] = None
