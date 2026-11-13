try:
    import pytest
except ImportError:
    pytest = None
from app.services.nlp_service import NLPService
from app.services.location_service import LocationService

def test_dynamic_equipment_day_vs_night():
    nlp = NLPService()

    scene_ext_day = {
        "scene_number": 1,
        "heading": "EXT. GATE / ROAD - DAY",
        "interior_exterior": "EXT",
        "location_name": "GATE / ROAD",
        "time_of_day": "DAY",
        "estimated_pages": 0.5,
        "action_text": "Marcus walks along the road under bright daylight.",
        "characters": ["MARCUS"],
        "dialogue_count": 1
    }

    scene_ext_night = {
        "scene_number": 2,
        "heading": "EXT. HARBOR PIER - NIGHT",
        "interior_exterior": "EXT",
        "location_name": "HARBOR PIER",
        "time_of_day": "NIGHT",
        "estimated_pages": 1.0,
        "action_text": "Dark fog over the pier as the truck crashes.",
        "characters": ["MARCUS"],
        "dialogue_count": 1
    }

    scene_int_day = {
        "scene_number": 3,
        "heading": "INT. PRODUCER ROOM - DAY",
        "interior_exterior": "INT",
        "location_name": "PRODUCER ROOM",
        "time_of_day": "DAY",
        "estimated_pages": 0.5,
        "action_text": "Morning sunlight streams through the windows as they talk.",
        "characters": ["PRODUCER", "DIRECTOR"],
        "dialogue_count": 3
    }

    scene_int_night = {
        "scene_number": 4,
        "heading": "INT. RESEARCH LAB - NIGHT",
        "interior_exterior": "INT",
        "location_name": "RESEARCH LAB",
        "time_of_day": "NIGHT",
        "estimated_pages": 1.0,
        "action_text": "Dark interior room with emergency terminal screens.",
        "characters": ["DR. VANCE"],
        "dialogue_count": 2
    }

    eq_ext_day, _ = nlp.extract_equipment(scene_ext_day, scene_ext_day["action_text"], 1)
    eq_ext_night, _ = nlp.extract_equipment(scene_ext_night, scene_ext_night["action_text"], 2)
    eq_int_day, _ = nlp.extract_equipment(scene_int_day, scene_int_day["action_text"], 3)
    eq_int_night, _ = nlp.extract_equipment(scene_int_night, scene_int_night["action_text"], 4)

    names_ext_day = [e["name"] for e in eq_ext_day]
    names_ext_night = [e["name"] for e in eq_ext_night]
    names_int_day = [e["name"] for e in eq_int_day]
    names_int_night = [e["name"] for e in eq_int_night]

    # EXT DAY assertions:
    # Uses natural sunlight bounce / butterfly silk / IRND filters
    assert any("Sun Bounce" in n for n in names_ext_day)
    assert any("Butterfly Silk" in n for n in names_ext_day)
    assert any("IRND" in n for n in names_ext_day)
    # Does NOT use heavy night fixtures or generators
    assert not any("1200W HMI" in n for n in names_ext_day)
    assert not any("Generator" in n for n in names_ext_day)
    assert not any("Key Light: High-Output" in n for n in names_ext_day)

    # EXT NIGHT assertions:
    # Requires 1200W HMI and generator for dark exterior
    assert any("1200W HMI" in n for n in names_ext_night)
    assert any("Generator" in n for n in names_ext_night)
    assert any("AC 12/3 Stinger" in n for n in names_ext_night)

    # INT DAY assertions:
    # Uses soft daylight fill and window gel balancing
    assert any("Soft Daylight Fill" in n for n in names_int_day)
    assert any("Window Daylight Balancing" in n for n in names_int_day)
    assert any("Foamcore Bounce" in n for n in names_int_day)
    # Does NOT have heavy night lighting
    assert not any("1200W HMI" in n for n in names_int_day)
    assert not any("Blackout Flags" in n for n in names_int_day)

    # INT NIGHT assertions:
    # Requires full controlled 3-point key/fill/rim and blackout
    assert any("Key Light: High-Output" in n for n in names_int_night)
    assert any("Blackout Flags" in n for n in names_int_night)
    assert any("Rim / Backlight" in n for n in names_int_night)
    assert any("Set Practical" in n for n in names_int_night)

def test_location_cost_calculations():
    # 1. Verify different locations get distinct, realistic costs
    cost_office = LocationService.calculate_location_cost("PROD OFC / RECEPTION", "INT", "DAY", scene_count=1, required_days=1, company_move_required=True)
    cost_producer = LocationService.calculate_location_cost("PRODUCTION HOUSE/PRODUCER ROOM", "INT", "DAY", scene_count=1, required_days=1, company_move_required=True)
    cost_door = LocationService.calculate_location_cost("PROD ROOM/DOOR", "INT", "DAY", scene_count=1, required_days=1, company_move_required=True)
    cost_gate_road = LocationService.calculate_location_cost("PROD HOUSE , GATE/ROAD", "EXT", "DAY", scene_count=1, required_days=1, company_move_required=True)
    cost_hospital = LocationService.calculate_location_cost("HOSPITAL / ER", "INT", "DAY", scene_count=2, required_days=1, company_move_required=True)

    # All costs should be different and non-trivial
    costs = [cost_office, cost_producer, cost_door, cost_gate_road, cost_hospital]
    assert len(set(costs)) == len(costs), f"Costs should all be distinct, got {costs}"

    # Specialized facility and exterior road with permits should cost more than a room doorway
    assert cost_hospital > cost_door
    assert cost_gate_road > cost_door

    # 2. Verify days scaling
    cost_1day = LocationService.calculate_location_cost("STUDIO A", "INT", "DAY", required_days=1)
    cost_3day = LocationService.calculate_location_cost("STUDIO A", "INT", "DAY", required_days=3)
    assert cost_3day > cost_1day * 2.0

    # 3. Verify night surcharge
    cost_day = LocationService.calculate_location_cost("WAREHOUSE", "INT", "DAY", required_days=1)
    cost_night = LocationService.calculate_location_cost("WAREHOUSE", "INT", "NIGHT", required_days=1)
    assert cost_night > cost_day

    # 4. Verify false location detection
    assert LocationService.is_false_location("ER")
    assert LocationService.is_false_location("ER-CUT")
    assert LocationService.is_false_location("INTERCUT")
    assert not LocationService.is_false_location("PROD OFC / RECEPTION")
