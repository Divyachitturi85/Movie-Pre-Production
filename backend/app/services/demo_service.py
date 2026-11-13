import logging
import re
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.script import Script
from app.models.scene import Scene
from app.models.character import Character
from app.models.location import Location
from app.models.production_element import ProductionElement
from app.models.schedule import Schedule
from app.models.shooting_day import ShootingDay
from app.models.scheduled_scene import ScheduledScene
from app.models.budget import Budget
from app.models.budget_item import BudgetItem
from app.models.call_sheet import CallSheet
from app.models.callback_letter import CallbackLetter
from app.models.explainability import AIExplainabilityRecord

from app.services.script_parser import ScriptParser
from app.services.nlp_service import NLPService
from app.services.complexity_service import ComplexityService
from app.services.scheduler_service import SchedulerService
from app.services.budget_service import BudgetService
from app.services.location_service import LocationService
from app.services.call_sheet_service import CallSheetService
from app.services.callback_service import CallbackService
from app.services.character_service import CharacterService, BLACKLIST, STANDALONE_TITLES

logger = logging.getLogger(__name__)

PROJECT_AURORA_SCREENPLAY = """PROJECT AURORA

Written by
Screenplay Division

FADE IN:

SCENE 1: INT. QUANTUM RESEARCH LAB - NIGHT

Emergency red warning lights pulse rhythmically. High-tech server racks flicker with static discharge. Smoke rolls across the reinforced titanium floor.

DR. ELENA VANCE (30s), wearing a torn lab coat with blood-stained cuffs, furiously types commands into a holographic terminal. Her hands tremble over the biometric scanner.

Beside her, the AURORA CORE—a levitating quantum containment sphere—glows with unstable violet plasma.

DR. ELENA VANCE
(into intercom)
Marcus! The containment magnetic field is collapsing! If we don't decouple the quantum drive in ninety seconds, the entire sector vaporizes!

A sudden explosive detonation rocks the laboratory! Sparks shower from overhead conduit pipes. Glass shards shatter across the cleanroom console.

Through the smoke, MARCUS REED (40s), clad in an armored tactical vest and holding a smoking pulse blaster, backs through the breached blast door.

MARCUS REED
We don't have ninety seconds, Elena! Chen's strike team just breached the perimeter! Grab the encryption drive!

Elena snatches a metallic quantum cylinder and slams it into a reinforced briefcase.

SCENE 2: EXT. LAB FACILITY SUB-LEVEL ROOF - NIGHT

Heavy torrential rain lashes against concrete parapets. Thunder rumbles in the pitch-black sky.

Elena and Marcus burst through the emergency roof exit. Below them, floodlights sweep the industrial compound.

A black tactical helicopter hovers overhead, its spotlight pinning them against the drenched brick wall.

AGENT CHEN (40s) steps into view from behind an HVAC housing, aiming an assault rifle equipped with laser scope. Four armored guards flank him with stun batons.

AGENT CHEN
Drop the briefcase, Dr. Vance. The Director requires the Aurora drive intact. You know there is nowhere to run.

MARCUS REED
(whispering to Elena)
When I fire, jump toward the maintenance crane.

Marcus triggers a blinding flash grenade! The helicopter pilot swerves as illumination flares. Gunfire erupts across the rooftop!

Elena sprints through the crossfire and leaps onto an automated service gondola.

SCENE 3: INT. UNDERGROUND METRO TUNNEL - NIGHT

Water drips into deep sewer grates. Distant subway trains rumble through the damp subterranean labyrinth.

Marcus and Elena stumble into an abandoned maintenance alcove. Marcus clutches a bloody wound on his shoulder.

Elena opens her medical first-aid kit, pulls out a sterile syringe and antiseptic spray, and dresses his wound.

MARCUS REED
(grimacing)
Chen has every federal frequency monitored. How long before the Aurora sequence initiates?

Elena retrieves an encrypted tablet from her backpack and connects a data cable to the quantum drive.

DR. ELENA VANCE
Fourteen hours until the singularity stabilizes. If Commander Hayes doesn't rendezvous at the harbor warehouse, the cascade cannot be reversed.

SCENE 4: INT. SYNDICATE COMMAND CENTER - NIGHT

A sterile, glass-walled conference room overlooking the neon skyline. Wall-sized holographic monitors display satellite tracking feeds and biometric heat signatures.

COMMANDER HAYES (50s), sharp tailored suit, watches the surveillance monitors with cold calculation.

Agent Chen enters, drenched from the rain, holding a damaged tracker beacon.

AGENT CHEN
We lost them in the subterranean canal network, Commander. But their biological signatures will surface near the industrial docks.

COMMANDER HAYES
Deploy the tactical drone swarm. Dr. Vance must not reach the harbor alive with that core. Authorize lethal force.

SCENE 5: EXT. INDUSTRIAL HARBOR DOCKS - DAWN

Thick morning fog clings to rows of rusted shipping containers. Gulls circle above brackish water. A lone cargo freighter idles near Pier 9.

Elena, now wearing a hooded trenchcoat, navigates through the maze of cargo containers. She checks a handheld GPS detector.

A sleek black hovercraft cruiser glides silently between the warehouses.

Elena ducks behind a forklift as two armed sentries patrol past with guard dogs.

SCENE 6: INT. PIER 9 WAREHOUSE - DAY

Dust motes drift in shafts of morning sunlight piercing through broken skylights. Rusted machinery and stacked wooden crates cast long shadows.

Elena steps cautiously into the open floor.

DR. ELENA VANCE
Commander Hayes? Are you here?

From the shadows behind a diesel generator, Commander Hayes steps forward, flanked by two bodyguards with suppressed pistols.

COMMANDER HAYES
You did remarkable work, Elena. Hand over the cylinder, and this can end peacefully.

Elena freezes, realizing the betrayal.

DR. ELENA VANCE
You were never planning an extraction. You sold the project to Chen's syndicate.

SCENE 7: EXT. HARBOR PIER - DAY

Marcus arrives in a stolen industrial utility truck, smashing through the chain-link gate!

The truck skids across the wet pier, slamming into Hayes's armored SUV!

A chaotic firefight erupts. Marcus fires from behind the open truck door, providing covering fire for Elena.

MARCUS REED
Elena, get to the boat! Move!

Elena sprints toward the moored tugboat as bullets ricochet off iron bollards.

SCENE 8: INT. TUGBOAT BRIDGE - DAY

Elena slams the steel hatch shut and throws the heavy latch.

She fires up the diesel engines. Gauges shudder to life.

Through the salt-encrusted forward windshield, she sees Agent Chen standing on the pier, raising a shoulder-mounted rocket launcher!

DR. ELENA VANCE
Not today.

She initiates the Aurora quantum pulse. A violet shockwave ripples outward from the cylinder, disabling all electrical circuits on the pier. The rocket launcher fizzles harmlessly.

The tugboat throttles into the open misty channel.

SCENE 9: EXT. COASTAL LIGHTHOUSE - DUSK

An isolated stone lighthouse stands resilient against battering ocean waves. The setting sun casts crimson streaks across the horizon.

Elena and a bandaged Marcus sit on the stone steps overlooking the Pacific. The glowing quantum cylinder rests securely between them, its hum finally quieted to a steady, harmless heartbeat.

MARCUS REED
So what happens now?

DR. ELENA VANCE
Now we rebuild. And we make sure nobody ever weaponizes Aurora again.

FADE OUT.
THE END
"""

class DemoService:
    """
    Initializes and populates 'Project Aurora' demo project with full
    production data, OR-Tools schedule, budget, call sheets, and callback letters.
    """

    def __init__(self):
        self.parser = ScriptParser()
        self.nlp = NLPService()
        self.complexity = ComplexityService()
        self.scheduler = SchedulerService()
        self.budget_service = BudgetService()
        self.call_sheet_service = CallSheetService()
        self.callback_service = CallbackService()

    def load_demo_project(self, db: Session) -> Project:
        """
        Creates or resets the demo project 'Project Aurora' with all pre-production data.
        """
        # Check if Project Aurora exists
        existing = db.query(Project).filter(Project.name == "Project Aurora").first()
        if existing:
            # Delete old demo project to refresh cleanly
            db.delete(existing)
            db.commit()

        project = Project(
            name="Project Aurora",
            description="High-stakes sci-fi thriller following quantum physicist Dr. Elena Vance and mercenary Marcus Reed as they protect a revolutionary energy core.",
            genre="Sci-Fi / Action Thriller",
            director="Denis Villeneuve (Demo Spec)",
            producer="Kathleen Kennedy (Demo Spec)",
            status="COMPLETED",
            current_stage="DOCUMENTS_GENERATED"
        )
        db.add(project)
        db.flush()

        # 1. Script Record
        script = Script(
            project_id=project.id,
            filename="Project_Aurora_Screenplay.pdf",
            file_path="./demo_data/Project_Aurora_Screenplay.pdf",
            file_size_bytes=142050,
            page_count=9,
            extraction_method="PDF_DIRECT",
            ocr_confidence=1.0,
            raw_text=PROJECT_AURORA_SCREENPLAY,
            cleaned_text=PROJECT_AURORA_SCREENPLAY
        )
        db.add(script)
        db.flush()

        # 2. Parse Scenes
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
                if sub_words and any(re.search(r'\b' + re.escape(sw) + r'\b', action_search) for sw in sub_words):
                    scene_chars.add(canon)

            final_scene_chars = sorted(list(scene_chars))
            sc_data["characters"] = final_scene_chars

            # Extract elements & audit via NLP
            elements, explains = self.nlp.extract_scene_elements(sc_data)
            score, level, factors, comp_explain = self.complexity.calculate_scene_complexity(sc_data, elements)

            # Store Explainability
            for exp in explains:
                rec = AIExplainabilityRecord(
                    project_id=project.id,
                    stage=exp.get("stage", "NLP"),
                    target_entity=exp.get("target_entity"),
                    input_data=exp.get("input_data"),
                    ai_method=exp.get("ai_method", "Transformer + spaCy"),
                    output_detected=exp.get("output_detected"),
                    confidence=exp.get("confidence", 0.9),
                    fallback_used=exp.get("fallback_used", False),
                    fallback_reason=exp.get("fallback_reason"),
                    details=exp.get("details", {})
                )
                db.add(rec)

            comp_rec = AIExplainabilityRecord(
                project_id=project.id,
                stage=comp_explain["stage"],
                target_entity=comp_explain["target_entity"],
                input_data=comp_explain["input_data"],
                ai_method=comp_explain["ai_method"],
                output_detected=comp_explain["output_detected"],
                confidence=comp_explain["confidence"],
                fallback_used=comp_explain["fallback_used"],
                details=comp_explain["details"]
            )
            db.add(comp_rec)

            scene_model = Scene(
                project_id=project.id,
                scene_number=sc_data.get("scene_number", sc_idx + 1),
                heading=sc_data.get("heading", ""),
                interior_exterior=sc_data.get("interior_exterior", "INT"),
                location_name=sc_data.get("location_name", "UNKNOWN"),
                time_of_day=sc_data.get("time_of_day", "DAY"),
                page_start=sc_idx + 1.0,
                page_end=sc_idx + 1.0 + sc_data.get("estimated_pages", 0.5),
                estimated_pages=sc_data.get("estimated_pages", 0.5),
                estimated_duration_minutes=sc_data.get("estimated_duration_minutes", 60),
                raw_content=sc_data.get("raw_content", ""),
                action_text=sc_data.get("action_text", ""),
                dialogue_count=sc_data.get("dialogue_count", 0),
                complexity_score=score,
                complexity_level=level,
                complexity_factors=factors,
                sequence_order=sc_idx + 1
            )
            db.add(scene_model)
            db.flush()
            scene_db_map[sc_data.get("scene_number", sc_idx + 1)] = scene_model

            # Save production elements
            for el in elements:
                pe = ProductionElement(
                    project_id=project.id,
                    scene_id=scene_model.id,
                    category=el.get("category", "PROP"),
                    name=el.get("name", "Asset"),
                    description=el.get("description", ""),
                    quantity=el.get("quantity", 1),
                    confidence=el.get("confidence", 0.88),
                    extraction_source=el.get("extraction_source", "NLP_SERVICE")
                )
                db.add(pe)
                all_elements_list.append(el)

            # Aggregate character presence
            for c_name in final_scene_chars:
                stat = character_stats.setdefault(c_name, {"scenes": [], "dialogues": 0})
                stat["scenes"].append(scene_model.scene_number)
                if c_name in scene_speakers or any(alias_map.get(sp) == c_name for sp in scene_speakers):
                    stat["dialogues"] += 2

            # Aggregate location stats
            raw_loc = sc_data.get("location_name", "UNKNOWN")
            loc_name = LocationService.canonicalize_location_name(raw_loc, scene_model.interior_exterior)
            l_stat = location_stats.setdefault(loc_name, {"scenes": [], "ie": scene_model.interior_exterior, "dn": scene_model.time_of_day})
            l_stat["scenes"].append(scene_model.scene_number)

        # 3. Create Characters
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
            character_models[c_name] = c_model

        # 4. Create Locations with dynamic realistic costs
        location_models = {}
        for loc_name, l_stat in location_stats.items():
            sc_cnt = len(l_stat["scenes"])
            req_days = max(1, (sc_cnt + 2) // 3)
            move_req = sc_cnt < 3
            calc_cost = LocationService.calculate_location_cost(
                name=loc_name,
                interior_exterior=l_stat["ie"],
                day_night=l_stat["dn"],
                scene_count=sc_cnt,
                required_days=req_days,
                company_move_required=move_req
            )
            desc = LocationService.get_location_description(loc_name, l_stat["ie"])

            loc_model = Location(
                project_id=project.id,
                name=loc_name,
                interior_exterior=l_stat["ie"],
                day_night=l_stat["dn"],
                scene_count=sc_cnt,
                required_days=req_days,
                company_move_required=move_req,
                estimated_cost=calc_cost,
                address_or_description=desc,
                scene_ids=l_stat["scenes"]
            )
            db.add(loc_model)
            location_models[loc_name] = loc_model

        # 5. Run OR-Tools CP-SAT Scheduling
        sched_res = self.scheduler.optimize_schedule(parsed_scenes, max_daily_hours=10.0)
        schedule = Schedule(
            project_id=project.id,
            name="Project Aurora - Master Shoot Schedule (OR-Tools)",
            total_days=sched_res["total_days"],
            total_shooting_hours=sched_res["total_hours"],
            total_company_moves=sched_res["total_company_moves"],
            optimization_status=sched_res["optimization_status"],
            solver_time_seconds=sched_res["solver_time_seconds"],
            objective_value=sched_res["objective_value"],
            notes=sched_res["explanation"]
        )
        db.add(schedule)
        db.flush()

        # Add shooting days and scheduled scenes
        day_models = []
        for d_data in sched_res.get("shooting_days", []):
            shoot_day = ShootingDay(
                schedule_id=schedule.id,
                day_number=d_data["day_number"],
                shoot_date=d_data["shoot_date"],
                call_time=d_data["call_time"],
                wrap_time=d_data["wrap_time"],
                meal_break_time=d_data["meal_break_time"],
                total_shooting_hours=d_data["total_shooting_hours"],
                company_moves_count=d_data["company_moves_count"],
                primary_location=d_data["primary_location"],
                cast_ids=d_data["cast_ids"],
                equipment_ids=d_data["equipment_ids"],
                notes=d_data["notes"]
            )
            db.add(shoot_day)
            db.flush()
            day_models.append((shoot_day, d_data))

            for s_item in d_data.get("scheduled_scenes", []):
                sc_id = s_item.get("scene_number", 1)
                sc_entity = scene_db_map.get(sc_id)
                sc_db_id = sc_entity.id if sc_entity else 1

                scheduled_scene = ScheduledScene(
                    shooting_day_id=shoot_day.id,
                    scene_id=sc_db_id,
                    sequence_order=s_item["sequence_order"],
                    estimated_start_time=s_item["estimated_start_time"],
                    estimated_duration_minutes=s_item["estimated_duration_minutes"],
                    setup_time_minutes=s_item["setup_time_minutes"],
                    location_name=s_item["location_name"],
                    company_move_before=s_item["company_move_before"]
                )
                db.add(scheduled_scene)

        # 6. Generate Budget
        b_data = self.budget_service.generate_initial_budget(
            shooting_days=sched_res["total_days"],
            cast_count=len(character_models),
            location_count=len(location_models),
            has_vfx=True
        )
        budget = Budget(
            project_id=project.id,
            currency=b_data["currency"],
            subtotal=b_data["subtotal"],
            contingency_rate=b_data["contingency_rate"],
            contingency_amount=b_data["contingency_amount"],
            tax_rate=b_data["tax_rate"],
            tax_amount=b_data["tax_amount"],
            grand_total=b_data["grand_total"],
            status="APPROVED",
            disclaimer=b_data["disclaimer"],
            notes=b_data["notes"]
        )
        db.add(budget)
        db.flush()

        for b_item in b_data.get("items", []):
            item_model = BudgetItem(
                budget_id=budget.id,
                category=b_item["category"],
                department=b_item["department"],
                account_code=b_item["account_code"],
                description=b_item["description"],
                quantity=b_item["quantity"],
                unit=b_item["unit"],
                unit_rate=b_item["unit_rate"],
                days_count=b_item["days_count"],
                subtotal=b_item["subtotal"],
                notes=b_item.get("notes")
            )
            db.add(item_model)

        # 7. Generate Call Sheets
        for shoot_day, d_data in day_models:
            cs_dict = self.call_sheet_service.generate_call_sheet_for_day(
                project_name=project.name,
                shooting_day=d_data,
                characters=[{"name": c} for c in character_models.keys()],
                elements=all_elements_list
            )
            call_sheet = CallSheet(
                project_id=project.id,
                shooting_day_id=shoot_day.id,
                day_number=cs_dict["day_number"],
                shoot_date=cs_dict["shoot_date"],
                general_call_time=cs_dict["general_call_time"],
                location_name=cs_dict["location_name"],
                location_address=cs_dict["location_address"],
                parking_info=cs_dict["parking_info"],
                weather_placeholder=cs_dict["weather_placeholder"],
                nearest_hospital=cs_dict["nearest_hospital"],
                scenes_summary=cs_dict["scenes_summary"],
                cast_calls=cs_dict["cast_calls"],
                crew_calls=cs_dict["crew_calls"],
                equipment_notes=cs_dict["equipment_notes"],
                props_costumes_notes=cs_dict["props_costumes_notes"],
                special_instructions=cs_dict["special_instructions"],
                meal_break=cs_dict["meal_break"],
                emergency_contact=cs_dict["emergency_contact"]
            )
            db.add(call_sheet)

        # 8. Generate Callback Letters
        char_list_for_callbacks = [
            {"name": c.name, "role": c.role, "id": c.id}
            for c in character_models.values()
        ]
        letters = self.callback_service.generate_bulk_letters(
            project_name=project.name,
            director=project.director,
            characters=char_list_for_callbacks
        )
        for l_data in letters:
            cb_model = CallbackLetter(
                project_id=project.id,
                character_id=l_data.get("character_id"),
                actor_name=l_data["actor_name"],
                actor_email=l_data.get("actor_email"),
                character_name=l_data["character_name"],
                role_type=l_data["role_type"],
                callback_date=l_data["callback_date"],
                callback_time=l_data["callback_time"],
                location=l_data["location"],
                sides_reference=l_data["sides_reference"],
                what_to_prepare=l_data["what_to_prepare"],
                contact_person=l_data["contact_person"],
                contact_email=l_data["contact_email"],
                contact_phone=l_data["contact_phone"],
                special_instructions=l_data.get("special_instructions"),
                letter_body=l_data["letter_body"],
                status="GENERATED"
            )
            db.add(cb_model)

        db.commit()
        db.refresh(project)
        logger.info(f"Project Aurora loaded successfully with {len(parsed_scenes)} scenes, {len(character_models)} characters, {sched_res['total_days']} shoot days, budget ${budget.grand_total:,.2f}.")
        return project
