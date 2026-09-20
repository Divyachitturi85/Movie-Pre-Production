import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CallbackService:
    """
    Service for generating professional Actor Callback Letters.
    Supports individual and bulk callback generation with customizable audition sides,
    session times, locations, and preparation instructions.
    """

    DEFAULT_TEMPLATE = """CONFIDENTIAL TALENT AUDITION CALLBACK

Production: {project_name}
Director: {director}
Casting Director: {contact_person}
Date: {callback_date}

Dear {actor_name},

Thank you for your fantastic initial audition for "{project_name}". On behalf of the director and producers, we are thrilled to invite you to an in-person / live callback session for the role of {character_name} ({role_type}).

============================================================
CALLBACK DETAILS:
============================================================
Date: {callback_date}
Time Slot: {callback_time}
Location: {location}
Sides to Prepare: {sides_reference}

============================================================
PREPARATION INSTRUCTIONS:
============================================================
{what_to_prepare}

Special Notes:
{special_instructions}

Please confirm your attendance within 24 hours of receiving this notification by replying to {contact_email} or calling {contact_phone}. If you have any scheduling conflicts with this allocated window, contact the casting department immediately so an alternate slot or virtual session can be arranged.

We look forward to working with you!

Warm regards,

{contact_person}
Head of Casting | {project_name} Production Office
Email: {contact_email}
Direct: {contact_phone}
"""

    def generate_letter(
        self,
        project_name: str,
        director: str,
        actor_name: str,
        character_name: str,
        role_type: str = "LEAD",
        callback_date: str = "Monday, October 12, 2026",
        callback_time: str = "10:30 AM EST",
        location: str = "Aurora Casting Studios, Studio 4B (120 Sunset Blvd) / Zoom",
        sides_reference: str = "Scene 2 (Lab Interrogation) & Scene 5 (Bridge Confrontation)",
        what_to_prepare: Optional[str] = None,
        contact_person: str = "Sarah Jenkins (Casting Director)",
        contact_email: str = "casting@auroraproductions.com",
        contact_phone: str = "+1 (555) 012-3456",
        special_instructions: Optional[str] = None,
        actor_email: Optional[str] = None,
        character_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generates an individual callback letter dictionary"""
        if not what_to_prepare:
            what_to_prepare = (
                "1. Please arrive 15 minutes prior to your designated slot.\n"
                "2. Have the attached sides memorized.\n"
                "3. You will be paired with the director for scene adjustments and chemistry reads."
            )

        if not special_instructions:
            special_instructions = (
                "Dress in casual wardrobe appropriate to the character's setting. "
                "No heavy green clothing due to chroma key tests on set."
            )

        body = self.DEFAULT_TEMPLATE.format(
            project_name=project_name,
            director=director or "TBD",
            actor_name=actor_name,
            character_name=character_name,
            role_type=role_type,
            callback_date=callback_date,
            callback_time=callback_time,
            location=location,
            sides_reference=sides_reference,
            what_to_prepare=what_to_prepare,
            special_instructions=special_instructions,
            contact_person=contact_person,
            contact_email=contact_email,
            contact_phone=contact_phone
        )

        return {
            "actor_name": actor_name,
            "actor_email": actor_email or f"{actor_name.lower().replace(' ', '.')}@talentagency.com",
            "character_id": character_id,
            "character_name": character_name,
            "role_type": role_type,
            "callback_date": callback_date,
            "callback_time": callback_time,
            "location": location,
            "sides_reference": sides_reference,
            "what_to_prepare": what_to_prepare,
            "contact_person": contact_person,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "special_instructions": special_instructions,
            "letter_body": body,
            "status": "GENERATED"
        }

    def generate_bulk_letters(
        self,
        project_name: str,
        director: str,
        characters: List[Dict[str, Any]],
        base_date: str = "Monday, October 12, 2026"
    ) -> List[Dict[str, Any]]:
        """
        Generates callback letters for all characters in the production with sequential time slots.
        """
        letters = []
        start_hour = 10
        start_minute = 0

        for idx, char in enumerate(characters):
            char_name = char.get("name", f"Character {idx+1}")
            role = char.get("role", "SUPPORTING")
            char_id = char.get("id")

            # Calculate sequential 30-minute audition slots
            slot_mins = start_minute + idx * 30
            slot_h = start_hour + (slot_mins // 60)
            slot_m = slot_mins % 60
            slot_time = f"{slot_h:02d}:{slot_m:02d} {'AM' if slot_h < 12 else 'PM'}"

            # Assigned candidate actor name placeholder
            actor_name = f"Candidate Actor {idx + 1}"
            scene_ref = f"Scenes involving {char_name} (Sides attached)"

            letter = self.generate_letter(
                project_name=project_name,
                director=director,
                actor_name=actor_name,
                character_name=char_name,
                role_type=role,
                callback_date=base_date,
                callback_time=slot_time,
                sides_reference=scene_ref,
                character_id=char_id
            )
            letters.append(letter)

        return letters
