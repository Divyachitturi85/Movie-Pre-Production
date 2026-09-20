import pytest
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
