import re
import logging
from typing import List, Dict, Any, Set, Tuple

logger = logging.getLogger(__name__)

# Words that indicate locations, props, camera/lighting, script formatting, or environment — NOT cast characters
BLACKLIST = {
    # Screenplay headings & locations
    'LAB', 'HARBOR', 'PIER', 'AURORA', 'PROJECT', 'DOCKS', 'METRO', 'TUNNEL', 
    'FACILITY', 'RESEARCH', 'LIGHTHOUSE', 'WAREHOUSE', 'BRIDGE', 'ROOM', 'GATE', 
    'ROAD', 'RECEPTION', 'TABLE', 'DESK', 'CHAIR', 'DOOR', 'SOFA', 'MIRROR', 
    'WATER', 'SCRIPT', 'PAPERS', 'CLOCK', 'WATCH', 'PHONE', 'BAG', 'MONTAGE', 
    'CLOSEUP', 'SHOT', 'THEME', 'MUSIC', 'TEXT', 'TIME', 'DAY', 'NIGHT', 
    'MORNING', 'EVENING', 'CONTINUOUS', 'END', 'SLOW', 'HIGH', 'LOW', 'MEDIUM',
    'EXTERIOR', 'INTERIOR', 'INT', 'EXT', 'SCENE', 'CUT', 'FADE', 'ALL', 'ALL 3',
    'OK', 'YES', 'NO', 'BUT', 'NEXT', 'EARLY', 'PROLOGUE', 'KADHA', 'MOODU', 'MUKKALA',
    'KACHITHAM', 'VASTHARA', 'PERU', 'MERU', 'MEELO', 'LEDU', 'GA', 'KI', 'NI', 
    'AHA', 'ANDHROO', 'MOTHAM', 'MUGGURU', 'GLASS', 'CORE', 'SET', 'STAGE', 'STUDIO',
    'STREET', 'CORRIDOR', 'HALLWAY', 'AREA', 'OFFICE', 'CABIN', 'DOORWAY', 'PROD', 'OFC',
    'HOUSE', 'BEDROOM', 'KITCHEN', 'BASEMENT', 'ROOFTOP', 'BALCONY', 'HIGHWAY', 'ALLEY',
    'CANOPY', 'ELEVATOR', 'STAIRWELL', 'PARKING', 'LOT', 'ENTRANCE', 'EXIT', 'WINDOW',
    'WALL', 'FLOOR', 'CEILING', 'GROUND', 'STATION', 'CENTER', 'HQ', 'HEADQUARTERS'
}

# Standalone titles and ranks that must not exist as standalone character names
STANDALONE_TITLES = {
    'AGENT', 'COMMANDER', 'DR', 'DR.', 'DOCTOR', 'PROFESSOR', 'OFFICER', 
    'CAPTAIN', 'GENERAL', 'CHIEF', 'SERGEANT', 'LIEUTENANT', 'COLONEL',
    'PRODUCER', 'DIRECTOR', 'MR', 'MRS', 'MS', 'SIR', 'MADAM', 'INSPECTOR',
    'DEPUTY', 'SHERIFF', 'DETECTIVE', 'PRESIDENT', 'MINISTER', 'WRITER'
}

class CharacterService:
    """
    Dedicated Screenplay Cast & Character Service:
    - Extracts verified dialogue speaker cues
    - Decomposes compound speaker cues ('VASU AND KALYAN', 'ALL 3 / VASU, VICKY AND KALYAN')
    - Filters out locations, props, technical screenplay terms, and isolated titles
    - Performs entity resolution & canonicalization (merging 'ELENA' and 'VANCE' into 'DR. ELENA VANCE')
    - Matches known cast in action paragraphs without spurious false-positives
    """

    CHARACTER_CUE_PATTERN = re.compile(
        r'^\s*([A-Z0-9_\'\.\s\-]{2,35})\s*(?:\(.*?\))?\s*$'
    )

    @classmethod
    def clean_name_token(cls, token: str) -> str:
        if not token:
            return ""
        t = re.sub(r'\(.*?\)', '', token).strip().upper()
        t = t.strip('.:-–—/ \'\t\n')
        # Slashed cues (e.g. SRUJAN/PRODUCER)
        if '/' in t:
            parts = [p.strip('.:-–—/ \'\t\n') for p in t.split('/')]
            non_titles = [p for p in parts if p not in STANDALONE_TITLES and p not in BLACKLIST]
            t = non_titles[0] if non_titles else parts[0]
        return t

    @classmethod
    def decompose_cue(cls, cue_str: str) -> List[str]:
        """Decomposes compound cues like 'VASU AND KALYAN' into individual cast names."""
        raw = cls.clean_name_token(cue_str)
        if not raw or raw in BLACKLIST or raw in STANDALONE_TITLES:
            return []
        
        # Remove 'ALL 3', 'ALL', etc.
        raw = re.sub(r'\bALL(\s+\d+)?\b', '', raw).strip('.:-–—/ \'\t\n')
        
        parts = re.split(r'\s+(?:AND|&|WITH)\s+|,\s*', raw)
        results = []
        for p in parts:
            p_clean = cls.clean_name_token(p)
            if p_clean and p_clean not in BLACKLIST and p_clean not in STANDALONE_TITLES:
                words = p_clean.split()
                # Exclude if contains core location words
                if not any(w in {'LAB', 'HARBOR', 'PIER', 'TUNNEL', 'DAY', 'NIGHT', 'ROAD', 'METRO', 'DOCKS'} for w in words):
                    results.append(p_clean)
        return results

    @classmethod
    def extract_speakers_from_text(cls, raw_text: str) -> List[str]:
        """Scans raw screenplay text for dialogue speaker cues."""
        if not raw_text:
            return []
        speakers = set()
        lines = raw_text.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Must look like an uppercase character cue
            if cls.CHARACTER_CUE_PATTERN.match(stripped):
                # Must not be a scene heading, transition, or technical mark
                if stripped.startswith(('INT', 'EXT', 'SCENE', 'CUT', 'FADE', 'SHOT', 'CLOSEUP', 'MONTAGE', 'DISSOLVE')):
                    continue
                # Verify that following non-empty line is dialogue or parenthetical
                is_speaker = False
                for next_line in lines[i+1:i+4]:
                    nl = next_line.strip()
                    if nl:
                        # Character cues precede spoken dialogue (which isn't all uppercase or is parenthetical)
                        if nl.startswith('(') or not nl.isupper() or len(nl.split()) > 3:
                            is_speaker = True
                        break
                if is_speaker:
                    for s in cls.decompose_cue(stripped):
                        speakers.add(s)
        return sorted(list(speakers))

    @classmethod
    def resolve_cast(cls, raw_candidates: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Subsumption merging and canonical name resolution:
        Merges sub-names and aliases (e.g. 'ELENA', 'VANCE') into the full canonical name ('DR. ELENA VANCE').
        Returns:
            - canonical_names: List of unique canonical character names
            - alias_map: Dict mapping every variant/sub-name to its canonical name
        """
        valid_cands = set()
        for item in raw_candidates:
            for c in cls.decompose_cue(item):
                if 2 <= len(c) <= 35:
                    valid_cands.add(c)

        # Sort descending by specificity (number of words, then character length)
        sorted_cands = sorted(list(valid_cands), key=lambda x: (len(x.split()), len(x)), reverse=True)
        canonical_map = {}
        canonical_names = []

        for name in sorted_cands:
            name_substantive = set(re.findall(r'\b[A-Z]+\b', name)) - STANDALONE_TITLES
            matched_canon = None
            
            for canon in canonical_names:
                canon_substantive = set(re.findall(r'\b[A-Z]+\b', canon)) - STANDALONE_TITLES
                if name_substantive and name_substantive.issubset(canon_substantive):
                    matched_canon = canon
                    break
            
            if matched_canon:
                canonical_map[name] = matched_canon
            else:
                canonical_names.append(name)
                canonical_map[name] = name

        return sorted(canonical_names), canonical_map

    @classmethod
    def resolve_character_stats(cls, raw_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Resolves raw character stats (scenes, dialogues) by merging aliases and purging non-character entities.
        """
        # First gather all raw candidate names
        all_raw_names = list(raw_stats.keys())
        canons, alias_map = cls.resolve_cast(all_raw_names)

        resolved = {}
        for canon in canons:
            resolved[canon] = {"scenes": set(), "dialogues": 0}

        for raw_name, stat in raw_stats.items():
            # Check if decomposed parts match canonical names
            for part in cls.decompose_cue(raw_name):
                canon = alias_map.get(part)
                if canon and canon in resolved:
                    resolved[canon]["scenes"].update(stat.get("scenes", []))
                    resolved[canon]["dialogues"] += stat.get("dialogues", 0)

        final_stats = {}
        for canon, data in resolved.items():
            sc_list = sorted(list(data["scenes"]))
            if sc_list:
                final_stats[canon] = {
                    "scenes": sc_list,
                    "dialogues": data["dialogues"]
                }
        return final_stats

    @classmethod
    def get_character_profile(cls, name: str, scene_count: int, dialogue_count: int, genre: str = "DRAMA") -> Dict[str, Any]:
        """Determines role tier, wardrobe requirements, and makeup continuity for a character."""
        role = "LEAD" if (scene_count >= 5 or dialogue_count >= 10) else ("SUPPORTING" if scene_count >= 2 else "MINOR")
        est_screen_time = round(max(scene_count * 3.5, dialogue_count * 0.8), 1)
        shoot_days = max(1, (scene_count + 1) // 2)

        g_upper = (genre or "").upper()
        n_upper = name.upper()

        if any(t in n_upper for t in ["AGENT", "COMMANDER", "OFFICER", "CAPTAIN", "SERGEANT"]) or "SCI-FI" in g_upper or "ACTION" in g_upper:
            costume = "Tactical / Field uniform with continuity weathering and communication headset"
            makeup = "Action continuity makeup (minor perspiration, grime, tactical wear)"
        elif any(t in n_upper for t in ["PRODUCER", "DIRECTOR", "DR", "EXECUTIVE"]) or "PRODUCER" in n_upper:
            costume = "Executive business casual / tailored office wardrobe with styled accessories"
            makeup = "Polished studio continuity makeup"
        else:
            costume = "Character wardrobe with scene-by-scene continuity alignment"
            makeup = "Standard continuity makeup"

        return {
            "role": role,
            "estimated_screen_time_minutes": est_screen_time,
            "required_shooting_days": shoot_days,
            "costume_requirements": costume,
            "makeup_requirements": makeup
        }

