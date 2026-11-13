import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BudgetService:
    """
    Film production budget estimation service inspired by industry standard
    chart of accounts (Movie Magic Budgeting workflow).
    
    Generates structured Above-The-Line and Below-The-Line line items,
    dynamically calculated from script elements and shooting days.
    """

    DEFAULT_DISCLAIMER = "Illustrative planning estimates — user configurable."

    def generate_initial_budget(
        self,
        shooting_days: int = 4,
        cast_count: int = 5,
        location_count: int = 4,
        has_vfx: bool = True,
        location_total_cost: float = None
    ) -> Dict[str, Any]:
        """
        Creates an initial comprehensive budget based on production parameters.
        """
        days = max(1, shooting_days)
        items = []

        # -------------------------------------------------------------
        # Above-The-Line (ATL)
        # -------------------------------------------------------------
        items.append({
            "category": "ABOVE_THE_LINE",
            "department": "Direction",
            "account_code": "1100",
            "description": "Director Fee (Pre-Prod, Prod, Post)",
            "quantity": 1.0,
            "unit": "Flat",
            "unit_rate": 25000.0,
            "days_count": 1.0,
            "subtotal": 25000.0,
            "notes": "Standard indie feature director agreement"
        })
        items.append({
            "category": "ABOVE_THE_LINE",
            "department": "Producers",
            "account_code": "1200",
            "description": "Producer / Line Producer Fee",
            "quantity": 2.0,
            "unit": "Flat",
            "unit_rate": 15000.0,
            "days_count": 1.0,
            "subtotal": 30000.0,
            "notes": "Executive Producer & Line Producer"
        })
        items.append({
            "category": "ABOVE_THE_LINE",
            "department": "Writing",
            "account_code": "1300",
            "description": "Screenplay Rights & Revisions",
            "quantity": 1.0,
            "unit": "Flat",
            "unit_rate": 12000.0,
            "days_count": 1.0,
            "subtotal": 12000.0,
            "notes": "Acquisition & production polish"
        })
        items.append({
            "category": "ABOVE_THE_LINE",
            "department": "Cast",
            "account_code": "1400",
            "description": "Principal Lead Cast Day Rates",
            "quantity": min(3.0, float(cast_count)),
            "unit": "Days",
            "unit_rate": 1200.0,
            "days_count": float(days),
            "subtotal": min(3.0, float(cast_count)) * 1200.0 * float(days),
            "notes": "SAG-AFTRA Modified Low Budget standard"
        })
        items.append({
            "category": "ABOVE_THE_LINE",
            "department": "Cast",
            "account_code": "1410",
            "description": "Supporting Cast Day Rates",
            "quantity": max(1.0, float(cast_count - 3)),
            "unit": "Days",
            "unit_rate": 650.0,
            "days_count": max(1.0, float(days - 1)),
            "subtotal": max(1.0, float(cast_count - 3)) * 650.0 * max(1.0, float(days - 1)),
            "notes": "Day player rate"
        })

        # -------------------------------------------------------------
        # Below-The-Line (BTL) - Production
        # -------------------------------------------------------------
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Camera",
            "account_code": "2000",
            "description": "Director of Photography (DP)",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 1500.0,
            "days_count": float(days),
            "subtotal": 1500.0 * float(days),
            "notes": "12-hour day rate"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Camera",
            "account_code": "2010",
            "description": "1st AC & 2nd AC Crew",
            "quantity": 2.0,
            "unit": "Days",
            "unit_rate": 600.0,
            "days_count": float(days),
            "subtotal": 1200.0 * float(days),
            "notes": "Focus puller and clapper loader"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Equipment Rental",
            "account_code": "2050",
            "description": "Camera Package (ARRI Alexa Mini LF + Prime Lenses)",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 1800.0,
            "days_count": float(days),
            "subtotal": 1800.0 * float(days),
            "notes": "Complete shooting kit with accessories"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Lighting & Grip",
            "account_code": "2100",
            "description": "Gaffer & Key Grip (Lighting Crew)",
            "quantity": 2.0,
            "unit": "Days",
            "unit_rate": 750.0,
            "days_count": float(days),
            "subtotal": 1500.0 * float(days),
            "notes": "Chief lighting technician and grip lead"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Lighting & Grip",
            "account_code": "2150",
            "description": "Grip & Electric Truck Package (3-Ton)",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 900.0,
            "days_count": float(days),
            "subtotal": 900.0 * float(days),
            "notes": "Includes HMI, LED arrays, stands, flags"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Sound",
            "account_code": "2200",
            "description": "Production Sound Mixer & Boom Op",
            "quantity": 2.0,
            "unit": "Days",
            "unit_rate": 700.0,
            "days_count": float(days),
            "subtotal": 1400.0 * float(days),
            "notes": "Multi-track recorder and wireless lavaliers"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Art Department",
            "account_code": "2300",
            "description": "Production Designer / Art Director",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 800.0,
            "days_count": float(days + 2),  # pre-dress days
            "subtotal": 800.0 * float(days + 2),
            "notes": "Includes set preparation and strike"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Art Department",
            "account_code": "2350",
            "description": "Props Purchase & Set Dressing Rentals",
            "quantity": 1.0,
            "unit": "Flat",
            "unit_rate": 5000.0,
            "days_count": 1.0,
            "subtotal": 5000.0,
            "notes": "Key hero props, practical effects dressing"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Costume & Wardrobe",
            "account_code": "2400",
            "description": "Costume Designer & Wardrobe Supervisor",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 650.0,
            "days_count": float(days + 1),
            "subtotal": 650.0 * float(days + 1),
            "notes": "Fittings and on-set changes"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Makeup & Hair",
            "account_code": "2500",
            "description": "Key Makeup Artist & SFX Prosthetics",
            "quantity": 1.0,
            "unit": "Days",
            "unit_rate": 700.0,
            "days_count": float(days),
            "subtotal": 700.0 * float(days),
            "notes": "Daily character makeup and touch-ups"
        })
        loc_unit_rate = 1800.0
        loc_subtotal = float(location_count) * loc_unit_rate
        if location_total_cost is not None and location_total_cost > 0:
            loc_subtotal = round(float(location_total_cost), 2)
            loc_unit_rate = round(loc_subtotal / max(1.0, float(location_count)), 2)

        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Locations",
            "account_code": "2600",
            "description": "Location Permits, Site Fees & Security",
            "quantity": float(location_count),
            "unit": "Flat",
            "unit_rate": loc_unit_rate,
            "days_count": 1.0,
            "subtotal": loc_subtotal,
            "notes": "Municipal permits, security, insurance riders & site rental"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Catering & Craft",
            "account_code": "2700",
            "description": "Cast & Crew Catering (Breakfast, Lunch, Crafty)",
            "quantity": 25.0,  # 25 headcount
            "unit": "Days",
            "unit_rate": 45.0,
            "days_count": float(days),
            "subtotal": 25.0 * 45.0 * float(days),
            "notes": "Full crew breakfast, hot lunch, all-day craft service"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Transportation",
            "account_code": "2800",
            "description": "Production Vans & Fuel Expense",
            "quantity": 2.0,
            "unit": "Days",
            "unit_rate": 350.0,
            "days_count": float(days),
            "subtotal": 700.0 * float(days),
            "notes": "Equipment transport and cast shuttle"
        })

        # -------------------------------------------------------------
        # Post-Production & VFX
        # -------------------------------------------------------------
        if has_vfx:
            items.append({
                "category": "BELOW_THE_LINE",
                "department": "VFX",
                "account_code": "3100",
                "description": "Visual Effects & CGI Composite Shots",
                "quantity": 12.0,
                "unit": "Units",
                "unit_rate": 1200.0,
                "days_count": 1.0,
                "subtotal": 14400.0,
                "notes": "Energy shields, holograms, muzzle flashes"
            })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Post-Production",
            "account_code": "3200",
            "description": "Picture Editorial & Sound Design / Mix",
            "quantity": 1.0,
            "unit": "Flat",
            "unit_rate": 18000.0,
            "days_count": 1.0,
            "subtotal": 18000.0,
            "notes": "Assembly, fine cut, Foley, 5.1 surround mix"
        })
        items.append({
            "category": "BELOW_THE_LINE",
            "department": "Insurance",
            "account_code": "3900",
            "description": "Production Package & Liability Insurance",
            "quantity": 1.0,
            "unit": "Flat",
            "unit_rate": 4500.0,
            "days_count": 1.0,
            "subtotal": 4500.0,
            "notes": "Equipment, general liability, workers comp"
        })

        # Calculate totals
        subtotal = sum(i["subtotal"] for i in items)
        contingency_rate = 0.10  # 10%
        contingency_amount = round(subtotal * contingency_rate, 2)
        tax_rate = 0.08          # 8%
        tax_amount = round((subtotal + contingency_amount) * tax_rate, 2)
        grand_total = round(subtotal + contingency_amount + tax_amount, 2)

        return {
            "currency": "INR",
            "subtotal": round(subtotal, 2),
            "contingency_rate": contingency_rate,
            "contingency_amount": contingency_amount,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "status": "APPROVED_ESTIMATE",
            "disclaimer": self.DEFAULT_DISCLAIMER,
            "notes": f"Auto-generated for {days} shooting days and {cast_count} cast members.",
            "items": items
        }

    def recalculate_totals(
        self,
        items: List[Dict[str, Any]],
        contingency_rate: float = 0.10,
        tax_rate: float = 0.08
    ) -> Dict[str, float]:
        """Recalculates subtotals, contingency, tax, and grand total"""
        subtotal = 0.0
        for item in items:
            q = float(item.get("quantity", 1.0))
            r = float(item.get("unit_rate", 0.0))
            d = float(item.get("days_count", 1.0))
            item_sub = round(q * r * d, 2)
            item["subtotal"] = item_sub
            subtotal += item_sub

        contingency = round(subtotal * contingency_rate, 2)
        tax = round((subtotal + contingency) * tax_rate, 2)
        grand_total = round(subtotal + contingency + tax, 2)

        return {
            "subtotal": round(subtotal, 2),
            "contingency_amount": contingency,
            "tax_amount": tax,
            "grand_total": grand_total
        }
