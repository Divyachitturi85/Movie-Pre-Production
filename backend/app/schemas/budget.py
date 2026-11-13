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
    actual_unit_rate: Optional[float] = None
    days_count: float
    subtotal: float
    actual_subtotal: Optional[float] = None
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
    actual_unit_rate: Optional[float] = None
    days_count: Optional[float] = None
    notes: Optional[str] = None

class BudgetResponse(BaseModel):
    id: int
    project_id: int
    currency: str
    subtotal: float
    actual_subtotal: Optional[float] = None
    contingency_rate: float
    contingency_amount: float
    actual_contingency_amount: Optional[float] = None
    tax_rate: float
    tax_amount: float
    actual_tax_amount: Optional[float] = None
    grand_total: float
    actual_grand_total: Optional[float] = None
    savings_amount: Optional[float] = None
    savings_percentage: Optional[float] = None
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
