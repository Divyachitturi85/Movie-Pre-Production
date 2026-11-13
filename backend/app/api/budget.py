from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.character import Character
from app.models.location import Location
from app.models.schedule import Schedule
from app.models.budget import Budget
from app.models.budget_item import BudgetItem
from app.models.explainability import AIExplainabilityRecord
from app.schemas.budget import BudgetResponse, BudgetItemUpdate, BudgetConfigUpdate
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/projects/{project_id}/budget", tags=["Budgeting"])

@router.post("/generate", response_model=BudgetResponse)
def generate_budget(project_id: int, db: Session = Depends(get_db)):
    """
    Generates an illustrative pre-production budget inspired by Movie Magic Budgeting.
    Includes Above-The-Line (Director, Producers, Cast, Writing) and
    Below-The-Line (Camera, Sound, Grip, Art, Costumes, Locations, VFX, Catering, Insurance).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sched = db.query(Schedule).filter(Schedule.project_id == project_id).first()
    days = sched.total_days if sched else 4
    cast_cnt = db.query(Character).filter(Character.project_id == project_id).count() or 5
    locations = db.query(Location).filter(Location.project_id == project_id).all()
    loc_cnt = len(locations) if locations else 4
    total_loc_cost = sum(l.estimated_cost for l in locations) if locations else None

    budget_svc = BudgetService()
    b_data = budget_svc.generate_initial_budget(
        shooting_days=days,
        cast_count=cast_cnt,
        location_count=loc_cnt,
        has_vfx=True,
        location_total_cost=total_loc_cost
    )

    # Delete existing budget if present
    db.query(Budget).filter(Budget.project_id == project_id).delete()

    budget = Budget(
        project_id=project_id,
        currency=b_data["currency"],
        subtotal=b_data["subtotal"],
        contingency_rate=b_data["contingency_rate"],
        contingency_amount=b_data["contingency_amount"],
        tax_rate=b_data["tax_rate"],
        tax_amount=b_data["tax_amount"],
        grand_total=b_data["grand_total"],
        status="ESTIMATED",
        disclaimer=b_data["disclaimer"],
        notes=b_data["notes"]
    )
    db.add(budget)
    db.flush()

    for item in b_data.get("items", []):
        bi = BudgetItem(
            budget_id=budget.id,
            category=item["category"],
            department=item["department"],
            account_code=item["account_code"],
            description=item["description"],
            quantity=item["quantity"],
            unit=item["unit"],
            unit_rate=item["unit_rate"],
            days_count=item["days_count"],
            subtotal=item["subtotal"],
            notes=item.get("notes")
        )
        db.add(bi)

    # Save AI Explainability record for Budget
    explain_rec = AIExplainabilityRecord(
        project_id=project_id,
        stage="BUDGET_ESTIMATION",
        target_entity=f"Production Budget (${budget.grand_total:,.2f})",
        input_data=f"{days} shoot days, {cast_cnt} cast, {loc_cnt} locations",
        ai_method="Industry Standard Chart of Accounts (Movie Magic Budgeting Workflow)",
        output_detected=f"Grand Total: ${budget.grand_total:,.2f} | Subtotal: ${budget.subtotal:,.2f} | Contingency: ${budget.contingency_amount:,.2f}",
        confidence=0.95,
        fallback_used=False,
        details={"items_count": len(b_data["items"])}
    )
    db.add(explain_rec)

    project.status = "BUDGETED"
    project.current_stage = "BUDGET_GENERATED"
    db.commit()
    db.refresh(budget)

    return enrich_budget_with_actuals(budget)

def enrich_budget_with_actuals(budget: Budget) -> Budget:
    actual_subtotal = 0.0
    for item in budget.items or []:
        markup = 1.15 if item.category == "ABOVE_THE_LINE" else 1.22
        actual_rate = round(item.unit_rate * markup, 2)
        actual_item_subtotal = round(item.quantity * actual_rate * item.days_count, 2)
        item.actual_unit_rate = actual_rate
        item.actual_subtotal = actual_item_subtotal
        actual_subtotal += actual_item_subtotal

    actual_subtotal = round(actual_subtotal, 2)
    c_rate = budget.contingency_rate if budget.contingency_rate is not None else 0.10
    t_rate = budget.tax_rate if budget.tax_rate is not None else 0.08
    actual_contingency = round(actual_subtotal * c_rate, 2)
    actual_tax = round((actual_subtotal + actual_contingency) * t_rate, 2)
    actual_grand_total = round(actual_subtotal + actual_contingency + actual_tax, 2)

    budget.actual_subtotal = actual_subtotal
    budget.actual_contingency_amount = actual_contingency
    budget.actual_tax_amount = actual_tax
    budget.actual_grand_total = actual_grand_total
    opt_gt = budget.grand_total or 0.0
    budget.savings_amount = round(max(0.0, actual_grand_total - opt_gt), 2)
    budget.savings_percentage = round((budget.savings_amount / actual_grand_total) * 100, 1) if actual_grand_total > 0 else 0.0
    return budget

@router.get("", response_model=BudgetResponse)
def get_budget(project_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.project_id == project_id).first()
    if not budget:
        # Auto-generate if not created yet
        return generate_budget(project_id, db)
    return enrich_budget_with_actuals(budget)

@router.put("/items", response_model=BudgetResponse)
def update_budget_items(
    project_id: int,
    payload: List[BudgetItemUpdate],
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(Budget.project_id == project_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    for upd in payload:
        if upd.id:
            item = db.query(BudgetItem).filter(BudgetItem.id == upd.id, BudgetItem.budget_id == budget.id).first()
            if item:
                if upd.description is not None:
                    item.description = upd.description
                if upd.quantity is not None:
                    item.quantity = upd.quantity
                if upd.unit_rate is not None:
                    item.unit_rate = upd.unit_rate
                if upd.days_count is not None:
                    item.days_count = upd.days_count
                if upd.notes is not None:
                    item.notes = upd.notes
                item.subtotal = round(item.quantity * item.unit_rate * item.days_count, 2)
        else:
            # Create new custom line item
            new_item = BudgetItem(
                budget_id=budget.id,
                category=upd.category or "BELOW_THE_LINE",
                department=upd.department or "Other",
                account_code=upd.account_code or "9900",
                description=upd.description or "Custom Item",
                quantity=upd.quantity or 1.0,
                unit=upd.unit or "Flat",
                unit_rate=upd.unit_rate or 0.0,
                days_count=upd.days_count or 1.0,
                subtotal=round((upd.quantity or 1.0) * (upd.unit_rate or 0.0) * (upd.days_count or 1.0), 2),
                is_custom=1,
                notes=upd.notes
            )
            db.add(new_item)

    db.flush()

    # Recalculate totals
    all_items = db.query(BudgetItem).filter(BudgetItem.budget_id == budget.id).all()
    subtotal = sum(i.subtotal for i in all_items)
    contingency = round(subtotal * budget.contingency_rate, 2)
    tax = round((subtotal + contingency) * budget.tax_rate, 2)
    grand_total = round(subtotal + contingency + tax, 2)

    budget.subtotal = subtotal
    budget.contingency_amount = contingency
    budget.tax_amount = tax
    budget.grand_total = grand_total

    db.commit()
    db.refresh(budget)
    return enrich_budget_with_actuals(budget)

@router.put("/config", response_model=BudgetResponse)
def update_budget_config(
    project_id: int,
    payload: BudgetConfigUpdate,
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(Budget.project_id == project_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if payload.contingency_rate is not None:
        budget.contingency_rate = payload.contingency_rate
    if payload.tax_rate is not None:
        budget.tax_rate = payload.tax_rate
    if payload.currency is not None:
        budget.currency = payload.currency

    # Recalculate
    contingency = round(budget.subtotal * budget.contingency_rate, 2)
    tax = round((budget.subtotal + contingency) * budget.tax_rate, 2)
    grand_total = round(budget.subtotal + contingency + tax, 2)

    budget.contingency_amount = contingency
    budget.tax_amount = tax
    budget.grand_total = grand_total

    db.commit()
    db.refresh(budget)
    return enrich_budget_with_actuals(budget)
