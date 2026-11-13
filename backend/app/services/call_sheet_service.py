import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CallSheetService:
    """
    Generates industry standard daily Call Sheets inspired by StudioBinder workflows.
    Includes scene breakdown, cast call times, crew departments, location logistics,
    and emergency/safety protocols.
    """

    KNOWN_ACTORS = {
        # Screenplay Characters (Telugu / Indie Feature)
        "VASU": "Naveen Polishetty",
        "KALYAN": "Priyadarshi Pulikonda",
        "VICKY": "Thiruveer",
        "SRUJAN": "Brahmaji",

        # Sci-Fi / Project Aurora Characters
        "DR. ELENA VANCE": "Rebecca Ferguson",
        "SARAH CHEN": "Gemma Chan",
        "MARCUS REID": "Oscar Isaac",
        "DIRECTOR KAUFMAN": "Giancarlo Esposito",
        "DR. CHEN": "Benedict Wong",
        "COMMANDER": "David Harbour"
    }

    DEFAULT_ACTORS_POOL = [
        "Vijay Varma", "Satyadev Kancharana", "Sundeep Kishan", "Rahul Ramakrishna",
        "Abhinav Gomatam", "Chaitanya Rao", "Murali Sharma", "Tanikella Bharani",
        "Naveen Chandra", "Harsha Chemudu", "Rohan Roy", "Aditya Menon",
        "Kavya Reddy", "Ananya Sharma", "Vikram Rathore", "Divya Spandana"
    ]

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
        day_scene_nums = [s.get("scene_number") for s in scheduled_scenes if s.get("scene_number") is not None]
        day_scene_set = set(day_scene_nums)
        
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

        # -------------------------------------------------------------
        # Cast Call Sheet Details: Real Characters & Real Actor Names
        # -------------------------------------------------------------
        # Filter characters that actually film today
        called_cast_list = []
        for c in characters:
            c_name = c.get("name", "").strip()
            # Ignore generic placeholders
            if not c_name or c_name.upper() in {"PROTAGONIST", "ANTAGONIST", "LEAD", "EXTRA"}:
                continue
            c_scenes = c.get("scene_ids") or []
            overlap = [sn for sn in c_scenes if sn in day_scene_set]
            if overlap:
                called_cast_list.append((c, overlap))

        # If no specific overlap found, include all project characters
        if not called_cast_list and characters:
            for c in characters:
                c_name = c.get("name", "").strip()
                if c_name and c_name.upper() not in {"PROTAGONIST", "ANTAGONIST", "LEAD", "EXTRA"}:
                    called_cast_list.append((c, day_scene_nums))

        cast_calls = []
        for idx, (c_dict, overlap_scs) in enumerate(called_cast_list):
            char_name = c_dict.get("name", f"Character {idx+1}")
            char_name_upper = char_name.upper().strip()

            # Realistic actor name resolution
            if char_name_upper in self.KNOWN_ACTORS:
                actor_name = self.KNOWN_ACTORS[char_name_upper]
            elif c_dict.get("actor_name"):
                actor_name = c_dict["actor_name"]
            else:
                actor_name = self.DEFAULT_ACTORS_POOL[idx % len(self.DEFAULT_ACTORS_POOL)]

            # Role formatting
            raw_role = (c_dict.get("role") or "LEAD").upper()
            role_label = "Lead Principal" if "LEAD" in raw_role else ("Supporting Lead" if "SUPPORTING" in raw_role else "Day Player")

            # Scenes scheduled today
            if overlap_scs:
                sorted_scs = sorted(overlap_scs)
                scenes_today_str = "Scenes " + ", ".join(f"#{num}" for num in sorted_scs)
            else:
                scenes_today_str = "All Day Scenes"

            # Staggered call times
            offset_mins = idx * 15
            pickup_h = 6 + (offset_mins // 60)
            pickup_m = offset_mins % 60
            pickup_time = f"{pickup_h:02d}:{pickup_m:02d} AM"

            hmu_m = (pickup_m + 30) % 60
            hmu_h = pickup_h + ((pickup_m + 30) // 60)
            hmu_time = f"{hmu_h:02d}:{hmu_m:02d} AM"

            onset_time = "07:45 AM" if idx == 0 else f"08:{min(55, idx * 15):02d} AM"

            # Wardrobe / costume info
            wardrobe_info = c_dict.get("costume_requirements") or f"Costume Change {day_num}: Script Day Continuity Wardrobe"

            cast_calls.append({
                "cast_id": idx + 1,
                "character_name": char_name,
                "actor_name": actor_name,
                "role": role_label,
                "scenes_today": scenes_today_str,
                "pickup": pickup_time,
                "hair_makeup": hmu_time,
                "wardrobe": wardrobe_info,
                "on_set": onset_time,
                "status": "CALLED",
                "notes": f"Sides for {scenes_today_str} attached; wireless lavalier mic check"
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

        # Extract props and weapons
        day_props = []
        day_weapons = []
        for el in elements:
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
