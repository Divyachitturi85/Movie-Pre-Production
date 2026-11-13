import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ScriptParser:
    """
    Robust screenplay parser supporting standard industry screenplay formats
    as well as variations, scanned texts, and custom formats.
    """

    HEADING_PATTERN = re.compile(
        r'^(?:(?:SCENE\s+)?(\d+)[\.:\s\-]+)?\s*(?:[A-Za-z]\.)?\s*(INT[\.\s/]+EXT[\.\s/]*|EXT[\.\s/]+INT[\.\s/]*|I[\.\s/]+E[\.\s/]*|INT[\.]*|EXT[\.]*)\s*(.*)$',
        re.IGNORECASE
    )

    STANDALONE_SCENE_NUM_PATTERN = re.compile(
        r'^(?:SCENE\s+)?(\d+)[\.:\s\-]*$',
        re.IGNORECASE
    )

    TOD_KEYWORDS = {
        'DAY', 'NIGHT', 'EVENING', 'MORNING', 'AFTERNOON', 'DUSK', 'DAWN',
        'TWILIGHT', 'SUNSET', 'SUNRISE', 'CONTINUOUS', 'CONT', 'LATER',
        'SAME TIME', 'MOMENTS LATER', 'EARLY MORNING', 'LATE NIGHT', 'NOON',
        'MIDDAY', 'MAGIC HOUR'
    }

    TRANSITION_PATTERN = re.compile(
        r'^\s*(FADE\s+IN:?|FADE\s+OUT:?|CUT\s+TO:?|DISSOLVE\s+TO:?|SMASH\s+CUT\s+TO:?|MATCH\s+CUT\s+TO:?|JUMP\s+CUT\s+TO:?|BACK\s+TO:?|BLACKOUT|THE\s+END|INTERCUT.*|INTER-CUT.*|INTER\s+CUT.*|END\s+INTERCUT.*|INT[\.\s\-]+ER[\-\s]?CUT.*)\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    CHARACTER_CUE_PATTERN = re.compile(
        r'^\s*([A-Z0-9_\'\.\s\-]{2,32})(?:\s*\((?:O\.S\.|V\.O\.|CONT\'D|CONTINUED|FILTERED)\))?\s*$'
    )

    PARENTHETICAL_PATTERN = re.compile(r'^\s*\([^\)]+\)\s*$')

    # Keywords that strongly indicate a title page / cover page scene (not a real scene)
    TITLE_PAGE_KEYWORDS = {
        'WRITTEN BY', 'ORIGINAL SCREENPLAY', 'BASED ON', 'FADE IN', 'FADE IN:',
        'DRAFT', 'REVISED DRAFT', 'SHOOTING SCRIPT', 'WGA', 'REGISTERED',
        'ALL RIGHTS RESERVED', 'COPYRIGHT', 'CONTACT', 'REPRESENTED BY',
        'PRODUCTION DRAFT', 'FINAL DRAFT', 'SECOND DRAFT', 'THIRD DRAFT',
        'FIRST DRAFT', 'TITLE PAGE', 'COVER PAGE'
    }

    def parse_heading_components(self, raw_line: str) -> Optional[Dict[str, Any]]:
        clean_line = (
            raw_line.replace('\u200b', '')
            .replace('\u200c', '')
            .replace('\u200d', '')
            .replace('\ufeff', '')
            .replace('\xa0', ' ')
            .replace('’', "'")
            .replace('‘', "'")
            .strip()
        )
        if not clean_line:
            return None

        m = self.HEADING_PATTERN.match(clean_line)
        if not m:
            sc_m = re.match(r'^(?:SCENE\s+)?(\d+)[\.:\s\-]+([A-Za-z0-9].*)$', clean_line, re.IGNORECASE)
            if sc_m:
                num_str, rest = sc_m.groups()
                sub_m = self.HEADING_PATTERN.match(rest.strip())
                if sub_m:
                    _, ie_type, sub_rest = sub_m.groups()
                    rest = sub_rest
                else:
                    ie_type = "INT"
            else:
                return None
        else:
            num_str, ie_type, rest = m.groups()

        rest = rest.strip()
        if not rest:
            return None

        parts = [p.strip() for p in re.split(r'[\-–—]+', rest) if p.strip()]
        if len(parts) == 0:
            loc = "UNKNOWN LOCATION"
            tod = "DAY"
        elif len(parts) == 1:
            words = parts[0].split()
            if len(words) > 1 and words[-1].upper() in self.TOD_KEYWORDS:
                loc = " ".join(words[:-1])
                tod = words[-1].upper()
            else:
                loc = parts[0]
                tod = "DAY"
        elif len(parts) == 2:
            loc = parts[0]
            tod = parts[1]
        else:
            last_upper = parts[-1].upper()
            second_last_upper = parts[-2].upper()
            if any(kw in last_upper for kw in self.TOD_KEYWORDS) and any(kw in second_last_upper for kw in self.TOD_KEYWORDS):
                loc = " - ".join(parts[:-2])
                tod = f"{parts[-2]} - {parts[-1]}"
            else:
                loc = " - ".join(parts[:-1])
                tod = parts[-1]

        loc_clean = re.sub(r'[\s/]+$', '', loc.strip('.:-–—/ ')).strip().upper()
        tod_clean = tod.strip('.:-–—/ ').upper()

        ie_clean = (ie_type or "INT").upper().replace('.', '').strip()
        if "EXT" in ie_clean and "INT" in ie_clean:
            ie_final = "INT/EXT"
        elif "EXT" in ie_clean:
            ie_final = "EXT"
        else:
            ie_final = "INT"

        return {
            "num_prefix": num_str,
            "ie_final": ie_final,
            "loc_clean": loc_clean or "MAIN SET",
            "time_clean": tod_clean or "DAY",
            "heading": clean_line
        }

    def _is_false_scene_heading(self, heading: str, loc: str, time_day: str) -> bool:
        """
        Determines whether a line matching HEADING_PATTERN is actually a false scene,
        such as an intercut directive, transition, or typo artifact.
        """
        h_upper = heading.upper().strip()
        loc_upper = (loc or "").upper().strip()
        tod_upper = (time_day or "").upper().strip()

        # Intercut patterns (e.g. INTER-CUT, INTERCUT, INT. ER-CUT, INTERCUT - DAY)
        if any(term in h_upper for term in ["INTERCUT", "INTER-CUT", "INTER CUT", "ER-CUT", "ERCUT", "END INTERCUT"]):
            return True

        # False locations that are actually transitions/cuts
        false_locations = {
            "ER", "ER-CUT", "ERCUT", "INTERCUT", "INTER-CUT", "CUT", "CUT TO",
            "SMASH CUT", "DISSOLVE", "TRANSITION"
        }
        if loc_upper in false_locations:
            return True

        # If time_of_day is a cut directive (e.g., from 'INT. ER - CUT')
        if tod_upper in {"CUT", "CUT END", "CUT TO"}:
            return True

        return False

    def parse_screenplay(self, script_text: str) -> List[Dict[str, Any]]:
        """
        Parses full script text into structured scenes.
        """
        if not script_text or not script_text.strip():
            return []

        # Pre-clean invisible format and zero-width unicode
        clean_text = (
            script_text.replace('\u200b', '')
            .replace('\u200c', '')
            .replace('\u200d', '')
            .replace('\ufeff', '')
            .replace('\xa0', ' ')
            .replace('’', "'")
            .replace('‘', "'")
        )

        lines = clean_text.split('\n')
        scenes: List[Dict[str, Any]] = []
        current_scene: Optional[Dict[str, Any]] = None
        scene_counter = 1

        current_speaker: Optional[str] = None
        current_dialogue_lines: List[str] = []
        current_action_lines: List[str] = []
        raw_scene_lines: List[str] = []
        total_dialogues_in_scene = 0

        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for scene heading
            h_comp = self.parse_heading_components(stripped)
            if h_comp:
                loc_clean = h_comp["loc_clean"]
                time_clean = h_comp["time_clean"]

                # Filter out transitions and intercut directives misclassified as scene headings
                if self._is_false_scene_heading(stripped, loc_clean, time_clean):
                    if current_scene is not None:
                        current_action_lines.append(stripped)
                        raw_scene_lines.append(line)
                    continue

                # Flush previous scene if exists
                if current_scene is not None:
                    current_scene["raw_content"] = "\n".join(raw_scene_lines)
                    current_scene["action_text"] = "\n".join(current_action_lines)
                    current_scene["dialogue_count"] = total_dialogues_in_scene
                    self._calculate_page_and_duration(current_scene, len(raw_scene_lines))
                    scenes.append(current_scene)

                # Initialize new scene
                num_prefix = h_comp["num_prefix"]
                scene_num = int(num_prefix) if num_prefix else scene_counter
                scene_counter = max(scene_counter + 1, scene_num + 1)

                current_scene = {
                    "scene_number": scene_num,
                    "heading": h_comp["heading"],
                    "interior_exterior": h_comp["ie_final"],
                    "location_name": loc_clean or "MAIN SET",
                    "time_of_day": time_clean or "DAY",
                    "characters": set(),
                    "dialogues": [],
                    "actions": []
                }
                raw_scene_lines = [stripped]
                current_action_lines = []
                current_speaker = None
                total_dialogues_in_scene = 0
                continue

            if current_scene is None:
                # Pre-slugline content (title page, author, date, logline, etc.)
                # Silently skip — do NOT create a fake scene for title/header text.
                continue

            raw_scene_lines.append(line)

            # Check for transitions
            if self.TRANSITION_PATTERN.match(stripped):
                current_speaker = None
                continue

            # Check for Character speaking cue
            char_match = self.CHARACTER_CUE_PATTERN.match(stripped)
            if char_match and not stripped.startswith(('INT', 'EXT', 'SCENE', 'CUT', 'FADE')) and len(stripped.split()) <= 4:
                char_name = char_match.group(1).strip().upper()
                # Clean parentheticals from name
                char_name = re.sub(r'\(.*?\)', '', char_name).strip()
                if char_name and len(char_name) > 1 and not char_name in ['CONTINUED', 'CONT\'D']:
                    current_speaker = char_name
                    current_scene["characters"].add(char_name)
                    total_dialogues_in_scene += 1
                    continue

            # Check parenthetical
            if self.PARENTHETICAL_PATTERN.match(stripped):
                continue

            # If inside dialogue
            if current_speaker and stripped:
                current_dialogue_lines.append(stripped)
                continue
            else:
                current_speaker = None
                if stripped:
                    current_action_lines.append(stripped)

        # Flush final scene
        if current_scene is not None:
            current_scene["raw_content"] = "\n".join(raw_scene_lines)
            current_scene["action_text"] = "\n".join(current_action_lines)
            current_scene["dialogue_count"] = total_dialogues_in_scene
            self._calculate_page_and_duration(current_scene, len(raw_scene_lines))
            scenes.append(current_scene)

        # Convert sets to sorted lists
        for sc in scenes:
            sc["characters"] = sorted(list(sc["characters"]))

        # --- Fallback: If no scenes matched standard sluglines, generate a unified scene ---
        if len(scenes) == 0 and script_text.strip():
            logger.warning("No standard sluglines matched; generating default scene for screenplay text.")
            fallback_scene = {
                "scene_number": 1,
                "heading": "SCENE 1: MAIN SEQUENCE - DAY",
                "interior_exterior": "INT",
                "location_name": "MAIN LOCATION",
                "time_of_day": "DAY",
                "characters": set(),
                "dialogues": [],
                "actions": []
            }
            for line in lines:
                s_line = line.strip()
                char_match = self.CHARACTER_CUE_PATTERN.match(s_line)
                if char_match and not s_line.startswith(('INT', 'EXT', 'SCENE', 'CUT', 'FADE')) and len(s_line.split()) <= 4:
                    char_name = re.sub(r'\(.*?\)', '', char_match.group(1)).strip().upper()
                    if char_name and len(char_name) > 1 and char_name not in ['CONTINUED', "CONT'D"]:
                        fallback_scene["characters"].add(char_name)
            fallback_scene["raw_content"] = script_text.strip()
            fallback_scene["action_text"] = script_text.strip()
            fallback_scene["dialogue_count"] = len(fallback_scene["characters"])
            self._calculate_page_and_duration(fallback_scene, len(lines))
            fallback_scene["characters"] = sorted(list(fallback_scene["characters"]))
            scenes.append(fallback_scene)

        # --- Post-processing: Remove title/cover page scenes & renumber ---
        scenes = self._remove_title_scenes(scenes)
        scenes = self._renumber_scenes(scenes)

        logger.info(f"Screenplay parsed successfully into {len(scenes)} scenes.")
        return scenes

    def _is_title_scene(self, scene: Dict[str, Any]) -> bool:
        """
        Detects if a scene is actually a title page / cover page, not a real scene.
        A title scene typically has:
          - No characters speaking
          - No dialogue
          - Short raw content (mostly metadata text)
          - Contains title-page keywords in its content
        """
        raw = (scene.get("raw_content", "") or "").upper()
        action = (scene.get("action_text", "") or "").upper()
        combined = raw + " " + action

        has_no_characters = len(scene.get("characters", [])) == 0
        has_no_dialogue = scene.get("dialogue_count", 0) == 0
        is_very_short = len(raw.strip()) < 300

        # Check for title page keywords in content
        has_title_keyword = any(kw in combined for kw in self.TITLE_PAGE_KEYWORDS)

        # A scene is a title scene if it has no characters, no dialogue,
        # is very short, AND contains at least one title-page keyword
        return has_no_characters and has_no_dialogue and is_very_short and has_title_keyword

    def _remove_title_scenes(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes leading title/cover page scenes from the scene list.
        Only checks the first 1-2 scenes to avoid removing real short scenes.
        """
        if not scenes:
            return scenes

        # Only strip title scenes from the very beginning (first scene only)
        removed = 0
        while scenes and removed < 2 and self._is_title_scene(scenes[0]):
            logger.info(f"Removing title/cover page scene: '{scenes[0].get('heading', '')}' — not a real scene.")
            scenes = scenes[1:]
            removed += 1

        return scenes

    def _renumber_scenes(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Renumbers all scenes sequentially starting from 1.
        Ensures scene_number and sequence_order are consistent.
        """
        for new_num, sc in enumerate(scenes, start=1):
            sc["scene_number"] = new_num
        return scenes

    def _calculate_page_and_duration(self, scene: Dict[str, Any], total_lines: int):
        """
        Calculates page count in 1/8ths and estimated shooting duration.
        """
        # Standard screenplay page ~ 54 lines
        pages = max(0.125, round(total_lines / 54.0, 2))
        scene["estimated_pages"] = pages
        
        # Base shooting duration: 1 page ~ 60 mins of shoot time
        # Minimum 20 minutes for very short insert shots
        shoot_mins = max(20, int(pages * 60))
        # Extra setup time if night scene
        if "NIGHT" in scene.get("time_of_day", ""):
            shoot_mins += 15
        scene["estimated_duration_minutes"] = shoot_mins
