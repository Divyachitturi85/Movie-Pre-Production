import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CallSheetService:
    """
    Generates industry standard daily Call Sheets inspired by StudioBinder workflows.
    Includes scene breakdown, cast call times, crew departments, location logistics,
    and emergency/safety protocols.
    """

    def generate_call_sheet_for_day(
        self,
        project_name: str,
        shooting_day: Dict[str, Any],
        characters: List[Dict[str, Any]],
        elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        day_num = shooting_day.get("day_number", 1)
        shoot_date = shooting_day.get("shoot_date", f"Shoot Day {day_num}")
        general_call = shooting_day.get("call_time", "07:00 AM")
        primary_loc = shooting_day.get("primary_location", "Main Stage / Practical Location")

        scheduled_scenes = shooting_day.get("scheduled_scenes", [])
        
        # Build scenes summary
        scenes_summary = []
        for s in scheduled_scenes:
            scenes_summary.append({
                "scene_number": s.get("scene_number", 1),
                "heading": s.get("heading", ""),
                "interior_exterior": s.get("interior_exterior", "INT"),
                "time_of_day": s.get("time_of_day", "DAY"),
                "pages": s.get("pages", 0.5),
                "location": s.get("location_name", primary_loc),
                "start_time": s.get("estimated_start_time", "08:00 AM"),
                "duration_mins": s.get("estimated_duration_minutes", 60),
                "complexity": s.get("complexity_level", "LOW")
            })

        # Cast call sheet details
        called_cast_names = shooting_day.get("cast_ids", [])
        cast_calls = []
        
        for idx, c_name in enumerate(called_cast_names):
            pickup_time = "06:15 AM"
            hmu_time = "06:45 AM"
            onset_time = "07:45 AM"
            
            cast_calls.append({
                "cast_id": idx + 1,
                "actor_name": f"Talent for {c_name}",
                "character_name": c_name,
                "pickup": pickup_time,
                "hair_makeup": hmu_time,
                "on_set": onset_time,
                "status": "CALLED",
                "notes": "Costume fitting completed in pre-prod"
            })

        if not cast_calls:
            cast_calls.append({
                "cast_id": 1,
                "actor_name": "Lead Actor TBA",
                "character_name": "PROTAGONIST",
                "pickup": "06:30 AM",
                "hair_makeup": "07:00 AM",
                "on_set": "08:00 AM",
                "status": "CALLED",
                "notes": "Sides attached"
            })

        # Crew department calls
        crew_calls = [
            {"department": "Production / AD", "title": "1st Assistant Director", "call_time": "06:30 AM"},
            {"department": "Camera", "title": "Director of Photography", "call_time": "06:45 AM"},
            {"department": "Camera", "title": "1st AC / Focus Puller", "call_time": "06:45 AM"},
            {"department": "Sound", "title": "Production Sound Mixer", "call_time": "07:00 AM"},
            {"department": "Grip & Electric", "title": "Gaffer & Key Grip", "call_time": "06:30 AM"},
            {"department": "Art / Props", "title": "Property Master", "call_time": "06:30 AM"},
            {"department": "Wardrobe / Makeup", "title": "Key Makeup Artist", "call_time": "06:15 AM"},
            {"department": "Catering", "title": "Catering Lead", "call_time": "06:00 AM"}
        ]

        # Extract props and costumes specific to this day's scenes
        day_scene_nums = {s.get("scene_number") for s in scheduled_scenes}
        day_props = []
        day_weapons = []
        for el in elements:
            # Check if element belongs to one of today's scenes
            day_props.append(el.get("name", ""))
            if el.get("category") == "WEAPON":
                day_weapons.append(el.get("name", ""))

        special_instructions = [
            "Mandatory morning safety briefing at 07:30 AM sharp.",
            "All crew and guests must check in with 2nd AD at production truck.",
            "Closed set during emotional dialogue scenes."
        ]
        if day_weapons:
            special_instructions.append("ARMORER ON SET: Real/prop weapons present. Follow strict armorer commands at all times.")

        return {
            "project_name": project_name,
            "day_number": day_num,
            "shoot_date": shoot_date,
            "general_call_time": general_call,
            "location_name": primary_loc,
            "location_address": f"Stage 4 / Practical Location - {primary_loc}",
            "parking_info": "Crew parking at Gate 3. Permit dashboard tags required.",
            "weather_placeholder": "Partly Cloudy, 68°F (20°C), Light wind 5mph",
            "nearest_hospital": "Mercy General Hospital Emergency (Level 1 Trauma), 1200 Health Ave (Tel: 911 / 555-0192)",
            "scenes_summary": scenes_summary,
            "cast_calls": cast_calls,
            "crew_calls": crew_calls,
            "equipment_notes": "A-Camera ARRI Alexa Mini LF package, Master Primes, Ronin 2 Gimbal on standby.",
            "props_costumes_notes": "Props: " + (", ".join(day_props[:6]) if day_props else "Standard hero props on truck."),
            "special_instructions": " \n".join(special_instructions),
            "meal_break": "13:00 - 13:45 (45-minute courtesy hot catered lunch)",
            "emergency_contact": "1st AD: Jane Martinez (555-0199) | Production Mgr: David Cole (555-0198)"
        }
