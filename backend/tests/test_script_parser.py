try:
    import pytest
except ImportError:
    pytest = None
from app.services.script_parser import ScriptParser

SAMPLE_SCRIPT = """
SCENE 1: INT. RESEARCH LAB - NIGHT

Dr. Vance types into the terminal.

DR. VANCE
The containment is failing!

Marcus aims his weapon.

MARCUS
We need to evacuate now!

SCENE 2: EXT. ROOFTOP - NIGHT

Rain falls heavily. A helicopter hovers above.
"""

def test_parse_screenplay_scenes():
    parser = ScriptParser()
    scenes = parser.parse_screenplay(SAMPLE_SCRIPT)
    
    assert len(scenes) == 2
    assert scenes[0]["scene_number"] == 1
    assert scenes[0]["interior_exterior"] == "INT"
    assert scenes[0]["time_of_day"] == "NIGHT"
    assert "DR. VANCE" in scenes[0]["characters"]
    assert "MARCUS" in scenes[0]["characters"]
    assert scenes[0]["dialogue_count"] == 2
    assert scenes[0]["estimated_pages"] > 0
    assert scenes[0]["estimated_duration_minutes"] > 0

    assert scenes[1]["scene_number"] == 2
    assert scenes[1]["interior_exterior"] == "EXT"

def test_intercut_rejection():
    parser = ScriptParser()
    script = """
SCENE 1: INT. PROD OFC / RECEPTION - DAY
Dr. Vance enters.

SCENE 2: INT. PROD ROOM/DOOR - DAY
They talk on phone.

INTER-CUT

Marcus answers in the field.

SCENE 3: INT. PROD H/Reception/PROD Room - DAY
More conversation.

INTER-CUT END

SCENE 4: INT. ER-CUT
Bogus heading if improperly parsed.

SCENE 5: EXT. GATE / ROAD - DAY
Final escape.
"""
    scenes = parser.parse_screenplay(script)
    headings = [s["heading"] for s in scenes]
    locations = [s["location_name"] for s in scenes]

    # Verify no scene has location 'ER', 'ER-CUT', or 'INTERCUT'
    assert "ER" not in locations
    assert "ER-CUT" not in locations
    assert "INTERCUT" not in locations

    # Verify scenes are numbered 1 to 4 sequentially
    for idx, sc in enumerate(scenes, start=1):
        assert sc["scene_number"] == idx

    # Verify true scenes are preserved
    assert any("PROD OFC" in loc for loc in locations)
    assert any("GATE" in loc for loc in locations)

def test_location_name_sanitization():
    parser = ScriptParser()
    script = """
SCENE 1: INT. RECEPTION AREA/ - DAY
Receptionist is seated.
"""
    scenes = parser.parse_screenplay(script)
    assert len(scenes) == 1
    assert scenes[0]["location_name"] == "RECEPTION AREA"
