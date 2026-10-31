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
        r'^(?:(?:SCENE\s+)?(\d+)[\.:\s]+)?\s*(INT\./EXT\.|EXT\./INT\.|INT\.|EXT\.|I/E\.|INT|EXT)\s+([^\n\-–—]+?)(?:\s*[\-–—]\s*([^\n]+))?$',
        re.IGNORECASE | re.MULTILINE
    )

    TRANSITION_PATTERN = re.compile(
        r'^\s*(FADE\s+IN:?|FADE\s+OUT:?|CUT\s+TO:?|DISSOLVE\s+TO:?|SMASH\s+CUT\s+TO:?|MATCH\s+CUT\s+TO:?|JUMP\s+CUT\s+TO:?|BACK\s+TO:?|BLACKOUT|THE\s+END)\s*$',
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

    def parse_screenplay(self, script_text: str) -> List[Dict[str, Any]]:
        """
        Parses full script text into structured scenes.
        """
        if not script_text or not script_text.strip():
            return []

        lines = script_text.split('\n')
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
            
            # Check for scene heading
            heading_match = self.HEADING_PATTERN.match(stripped)
            if heading_match:
                # Flush previous scene if exists
                if current_scene is not None:
                    current_scene["raw_content"] = "\n".join(raw_scene_lines)
                    current_scene["action_text"] = "\n".join(current_action_lines)
                    current_scene["dialogue_count"] = total_dialogues_in_scene
                    self._calculate_page_and_duration(current_scene, len(raw_scene_lines))
                    scenes.append(current_scene)

                # Initialize new scene
                num_prefix, ie_type, loc, time_day = heading_match.groups()
                scene_num = int(num_prefix) if num_prefix else scene_counter
                scene_counter = max(scene_counter + 1, scene_num + 1)

                ie_clean = ie_type.upper().replace('.', '').strip()
                if "EXT" in ie_clean and "INT" in ie_clean:
                    ie_final = "INT/EXT"
                elif "EXT" in ie_clean:
                    ie_final = "EXT"
                else:
                    ie_final = "INT"

                loc_clean = (loc or "UNKNOWN LOCATION").strip().upper()
                time_clean = (time_day or "DAY").strip().upper()

                current_scene = {
                    "scene_number": scene_num,
                    "heading": stripped,
                    "interior_exterior": ie_final,
                    "location_name": loc_clean,
                    "time_of_day": time_clean,
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
