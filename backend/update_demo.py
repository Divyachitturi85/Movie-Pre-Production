import re

file_path = 'backend/app/services/demo_service.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import re and CharacterService
if 'import re' not in content:
    content = content.replace('import logging', 'import logging\nimport re')

if 'CharacterService' not in content:
    content = content.replace(
        'from app.services.callback_service import CallbackService',
        'from app.services.callback_service import CallbackService\nfrom app.services.character_service import CharacterService, BLACKLIST, STANDALONE_TITLES'
    )

old_parse_section = """        # 2. Parse Scenes
        parsed_scenes = self.parser.parse_screenplay(PROJECT_AURORA_SCREENPLAY)
        scene_db_map = {}
        all_elements_list = []
        character_stats = {}
        location_stats = {}

        for sc_idx, sc_data in enumerate(parsed_scenes):
            # Extract elements & audit via NLP
            elements, explains = self.nlp.extract_scene_elements(sc_data)"""

new_parse_section = """        # 2. Parse Scenes
        parsed_scenes = self.parser.parse_screenplay(PROJECT_AURORA_SCREENPLAY)
        scene_db_map = {}
        all_elements_list = []
        character_stats = {}
        location_stats = {}

        # Discover canonical cast from dialogue cues across screenplay
        all_raw_cues = []
        for sc_data in parsed_scenes:
            cues = CharacterService.extract_speakers_from_text(sc_data.get("raw_content", ""))
            all_raw_cues.extend(cues)
        canonical_cast, alias_map = CharacterService.resolve_cast(all_raw_cues)

        for sc_idx, sc_data in enumerate(parsed_scenes):
            # Discover canonical characters in this scene
            scene_speakers = CharacterService.extract_speakers_from_text(sc_data.get("raw_content", ""))
            scene_chars = set()
            for sp in scene_speakers:
                canon = alias_map.get(sp)
                if canon and canon not in BLACKLIST and canon not in STANDALONE_TITLES:
                    scene_chars.add(canon)

            action_search = f"{sc_data.get('action_text', '')} {sc_data.get('raw_content', '')}".lower()
            for canon in canonical_cast:
                sub_words = [w.lower() for w in canon.split() if w not in STANDALONE_TITLES and len(w) > 2]
                if sub_words and any(re.search(r'\\b' + re.escape(sw) + r'\\b', action_search) for sw in sub_words):
                    scene_chars.add(canon)

            final_scene_chars = sorted(list(scene_chars))
            sc_data["characters"] = final_scene_chars

            # Extract elements & audit via NLP
            elements, explains = self.nlp.extract_scene_elements(sc_data)"""

old_agg_section = """            # Aggregate character presence
            for c_name in sc_data.get("characters", []):
                stat = character_stats.setdefault(c_name, {"scenes": [], "dialogues": 0})
                stat["scenes"].append(scene_model.scene_number)
                stat["dialogues"] += 2"""

new_agg_section = """            # Aggregate character presence
            for c_name in final_scene_chars:
                stat = character_stats.setdefault(c_name, {"scenes": [], "dialogues": 0})
                stat["scenes"].append(scene_model.scene_number)
                if c_name in scene_speakers or any(alias_map.get(sp) == c_name for sp in scene_speakers):
                    stat["dialogues"] += 2"""

old_char_section = """        # 3. Create Characters
        character_models = {}
        for c_name, stat in character_stats.items():
            sc_count = len(stat["scenes"])
            role = "LEAD" if sc_count >= 5 else ("SUPPORTING" if sc_count >= 2 else "MINOR")
            c_model = Character(
                project_id=project.id,
                name=c_name,
                role=role,
                scene_count=sc_count,
                dialogue_count=stat["dialogues"],
                estimated_screen_time_minutes=round(sc_count * 3.5, 1),
                required_shooting_days=max(1, (sc_count + 1) // 2),
                costume_requirements="Tactical / Scientist wardrobe with continuity weathering",
                makeup_requirements="Stunt blood, bruising, sweat continuity" if "MARCUS" in c_name or "ELENA" in c_name else "Standard character makeup",
                scene_ids=stat["scenes"]
            )
            db.add(c_model)
            db.flush()
            character_models[c_name] = c_model"""

new_char_section = """        # 3. Create Characters
        resolved_char_stats = CharacterService.resolve_character_stats(character_stats)
        character_models = {}
        for c_name, stat in resolved_char_stats.items():
            sc_count = len(stat["scenes"])
            profile = CharacterService.get_character_profile(
                name=c_name,
                scene_count=sc_count,
                dialogue_count=stat["dialogues"],
                genre=project.genre
            )
            c_model = Character(
                project_id=project.id,
                name=c_name,
                role=profile["role"],
                scene_count=sc_count,
                dialogue_count=stat["dialogues"],
                estimated_screen_time_minutes=profile["estimated_screen_time_minutes"],
                required_shooting_days=profile["required_shooting_days"],
                costume_requirements=profile["costume_requirements"],
                makeup_requirements=profile["makeup_requirements"],
                scene_ids=stat["scenes"]
            )
            db.add(c_model)
            db.flush()
            character_models[c_name] = c_model"""

# Normalize CRLF
content_norm = content.replace('\r\n', '\n')
old_parse_section_norm = old_parse_section.replace('\r\n', '\n')
old_agg_section_norm = old_agg_section.replace('\r\n', '\n')
old_char_section_norm = old_char_section.replace('\r\n', '\n')

assert old_parse_section_norm in content_norm, 'old_parse_section not found'
assert old_agg_section_norm in content_norm, 'old_agg_section not found'
assert old_char_section_norm in content_norm, 'old_char_section not found'

content_norm = content_norm.replace(old_parse_section_norm, new_parse_section)
content_norm = content_norm.replace(old_agg_section_norm, new_agg_section)
content_norm = content_norm.replace(old_char_section_norm, new_char_section)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Updated demo_service.py successfully!")

