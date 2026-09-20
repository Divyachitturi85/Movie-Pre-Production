import pytest
from app.services.budget_service import BudgetService

def test_budget_generation_and_recalculation():
    budget_svc = BudgetService()
    budget = budget_svc.generate_initial_budget(shooting_days=5, cast_count=6, location_count=3, has_vfx=True)

    assert budget["subtotal"] > 0
    assert budget["contingency_rate"] == 0.10
    assert budget["contingency_amount"] == round(budget["subtotal"] * 0.10, 2)
    assert budget["grand_total"] > budget["subtotal"]
    assert len(budget["items"]) > 10

    # Recalculate test
    recalc = budget_svc.recalculate_totals(budget["items"], contingency_rate=0.15, tax_rate=0.05)
    assert recalc["subtotal"] == budget["subtotal"]
    assert recalc["contingency_amount"] == round(budget["subtotal"] * 0.15, 2)
