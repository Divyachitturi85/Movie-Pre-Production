with open('backend/app/services/document_service.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "f\"Estimated production budget: <b>${budget.get('grand_total', 0.0):,.2f}</b> ({budget.get('disclaimer', '')}).\"",
    "f\"Estimated production budget: <b>INR {budget.get('grand_total', 0.0):,.2f}</b> ({budget.get('disclaimer', '')}).\""
)
c = c.replace(
    '["Cast Members", str(stats.get(\'character_count\', 0)), "Est. Budget Subtotal", f"${budget.get(\'subtotal\', 0.0):,.2f}"],',
    '["Cast Members", str(stats.get(\'character_count\', 0)), "Est. Budget Subtotal", f"INR {budget.get(\'subtotal\', 0.0):,.2f}"],'
)
c = c.replace(
    '["Locations", str(stats.get(\'location_count\', 0)), "Contingency (10%)", f"${budget.get(\'contingency_amount\', 0.0):,.2f}"],',
    '["Locations", str(stats.get(\'location_count\', 0)), "Contingency (10%)", f"INR {budget.get(\'contingency_amount\', 0.0):,.2f}"],'
)
c = c.replace(
    '["Total Props", str(stats.get(\'props_count\', 0)), "Taxes & Permits (8%)", f"${budget.get(\'tax_amount\', 0.0):,.2f}"],',
    '["Total Props", str(stats.get(\'props_count\', 0)), "Taxes & Permits (8%)", f"INR {budget.get(\'tax_amount\', 0.0):,.2f}"],'
)
c = c.replace(
    '["Costumes / Wardrobe", str(stats.get(\'costumes_count\', 0)), "Grand Total Budget", f"${budget.get(\'grand_total\', 0.0):,.2f}"]',
    '["Costumes / Wardrobe", str(stats.get(\'costumes_count\', 0)), "Grand Total Budget", f"INR {budget.get(\'grand_total\', 0.0):,.2f}"]'
)
c = c.replace(
    'headers = ["Category", "Department", "Code", "Description", "Quantity", "Unit", "Rate ($)", "Days", "Subtotal ($)", "Notes"]',
    'headers = ["Category", "Department", "Code", "Description", "Quantity", "Unit", "Rate (INR)", "Days", "Subtotal (INR)", "Notes"]'
)
c = c.replace(
    '["Location Name", "I/E", "D/N", "Scenes Count", "Required Days", "Company Move Required", "Est Cost ($)"],',
    '["Location Name", "I/E", "D/N", "Scenes Count", "Required Days", "Company Move Required", "Est Cost (INR)"],'
)

with open('backend/app/services/document_service.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated document_service.py successfully')
