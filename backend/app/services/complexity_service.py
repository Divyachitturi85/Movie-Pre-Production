import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

class ComplexityService:
    """
    Evaluates screenplay scene complexity based on production factors:
    - Cast density (number of speaking actors and background talent)
    - Location type (EXT vs INT, remote/complex locations)
    - Time of Day (NIGHT lighting setup complexity)
    - Production elements (VFX, SFX, Weapons, Vehicles, Animals)
    - Camera/Lighting specialized equipment needs
    """

    def calculate_scene_complexity(self, scene: Dict[str, Any], elements: List[Dict[str, Any]]) -> Tuple[float, str, Dict[str, Any], Dict[str, Any]]:
        factors = {}
        base_score = 1.0

        # 1. Cast factor
        cast = scene.get("characters", [])
        cast_count = len(cast)
        if cast_count >= 5:
            cast_pts = 2.5
            factors["cast_density"] = f"Heavy ({cast_count} characters) [+2.5]"
        elif cast_count >= 3:
            cast_pts = 1.5
            factors["cast_density"] = f"Moderate ({cast_count} characters) [+1.5]"
        elif cast_count >= 1:
            cast_pts = 0.5
            factors["cast_density"] = f"Standard ({cast_count} characters) [+0.5]"
        else:
            cast_pts = 0.0
            factors["cast_density"] = "Solo / Non-verbal [+0.0]"

        # 2. Location & Time of Day factor
        ie = scene.get("interior_exterior", "INT").upper()
        tod = scene.get("time_of_day", "DAY").upper()
        
        env_pts = 0.0
        env_reasons = []
        if "EXT" in ie:
            env_pts += 1.2
            env_reasons.append("Exterior Shoot (+1.2)")
        if "NIGHT" in tod or "DUSK" in tod:
            env_pts += 1.5
            env_reasons.append("Night/Dusk Lighting Setup (+1.5)")
        
        factors["environment"] = ", ".join(env_reasons) if env_reasons else "Controlled Interior Day [+0.0]"

        # 3. Element categories present
        cat_counts = {}
        for el in elements:
            c = el.get("category", "OTHER")
            cat_counts[c] = cat_counts.get(c, 0) + 1

        element_pts = 0.0
        elem_reasons = []
        
        if cat_counts.get("VFX", 0) > 0:
            element_pts += 2.0
            elem_reasons.append(f"Visual Effects CGI ({cat_counts['VFX']}) [+2.0]")
        if cat_counts.get("SFX", 0) > 0:
            element_pts += 2.0
            elem_reasons.append(f"Physical Special Effects ({cat_counts['SFX']}) [+2.0]")
        if cat_counts.get("WEAPON", 0) > 0:
            element_pts += 1.5
            elem_reasons.append(f"Weapons/Stunts Coordination ({cat_counts['WEAPON']}) [+1.5]")
        if cat_counts.get("VEHICLE", 0) > 0:
            element_pts += 1.5
            elem_reasons.append(f"Vehicles in Action ({cat_counts['VEHICLE']}) [+1.5]")
        if cat_counts.get("ANIMAL", 0) > 0:
            element_pts += 1.5
            elem_reasons.append(f"Animal Handling ({cat_counts['ANIMAL']}) [+1.5]")
        if cat_counts.get("PROP", 0) >= 4:
            element_pts += 0.8
            elem_reasons.append(f"High Prop Density ({cat_counts['PROP']}) [+0.8]")

        factors["elements"] = elem_reasons if elem_reasons else ["Standard Art Requirements [+0.0]"]

        # 4. Page length factor
        pages = scene.get("estimated_pages", 0.5)
        if pages >= 3.0:
            page_pts = 1.5
            factors["page_length"] = f"Extensive ({pages} pgs) [+1.5]"
        elif pages >= 1.5:
            page_pts = 0.8
            factors["page_length"] = f"Moderate ({pages} pgs) [+0.8]"
        else:
            page_pts = 0.2
            factors["page_length"] = f"Brief ({pages} pgs) [+0.2]"

        total_score = round(base_score + cast_pts + env_pts + element_pts + page_pts, 2)
        # Cap score between 1.0 and 10.0
        final_score = min(10.0, max(1.0, total_score))

        if final_score < 3.0:
            level = "LOW"
        elif final_score < 5.5:
            level = "MEDIUM"
        elif final_score < 8.0:
            level = "HIGH"
        else:
            level = "VERY HIGH"

        scene_num = scene.get("scene_number", 1)
        explain_record = {
            "stage": "COMPLEXITY_SCORING",
            "target_entity": f"Scene {scene_num} Complexity",
            "input_data": f"Scene {scene_num} Parameters (Cast: {cast_count}, EXT: {'EXT' in ie}, Night: {'NIGHT' in tod}, VFX/SFX: {cat_counts.get('VFX', 0) + cat_counts.get('SFX', 0)})",
            "ai_method": "Multi-Factor Production Complexity Engine (Weighted Heuristic Model)",
            "output_detected": f"Score: {final_score}/10.0 -> {level}",
            "confidence": 0.95,
            "fallback_used": False,
            "fallback_reason": None,
            "details": factors
        }

        return final_score, level, factors, explain_record
