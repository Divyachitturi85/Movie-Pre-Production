import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LocationService:
    """
    Service for analyzing screenplay filming locations, categorizing sets,
    and calculating realistic, dynamic estimated site permit and rental costs.
    """

    # Keyword classifiers for location tiers
    TIER_KEYWORDS = {
        "SPECIALIZED": [
            "HOSPITAL", "ER", "EMERGENCY", "CLINIC", "LAB", "LABORATORY",
            "COURT", "COURTHOUSE", "POLICE", "PRECINCT", "PRISON", "JAIL",
            "AIRPORT", "HANGAR", "BANK", "VAULT", "STUDIO", "STAGE", "SOUNDSTAGE"
        ],
        "PUBLIC_EXTERIOR": [
            "ROAD", "STREET", "HIGHWAY", "GATE", "ALLEY", "PARK", "HARBOR",
            "PIER", "BRIDGE", "BEACH", "DOCK", "ROOFTOP", "FOREST", "WOODS",
            "AVENUE", "LANE", "OUTSIDE"
        ],
        "EXECUTIVE_COMMERCIAL": [
            "PRODUCTION HOUSE", "PROD HOUSE", "PRODUCER ROOM", "PROD ROOM",
            "OFFICE", "BOARDROOM", "CONFERENCE", "EXECUTIVE", "HEADQUARTERS",
            "HQ", "HOTEL", "RESTAURANT", "BAR", "CLUB", "CAFE"
        ],
        "RESIDENTIAL": [
            "HOUSE", "HOME", "APARTMENT", "FLAT", "BEDROOM", "LIVING ROOM",
            "KITCHEN", "BALCONY", "MANSION", "VILLA", "BUNGALOW", "ESTATE"
        ],
        "COMPACT_SECONDARY": [
            "RECEPTION", "DOOR", "CORRIDOR", "HALLWAY", "LOBBY", "ENTRANCE",
            "STAIRWELL", "ELEVATOR", "FOYER", "SRUJAN ROOM", "ROOM", "CABIN", "BOOTH"
        ]
    }

    @classmethod
    def sanitize_location_name(cls, name: str) -> str:
        """
        Cleans location names: strips trailing slashes, punctuation,
        and excessive whitespace (e.g. 'RECEPTION AREA/' -> 'RECEPTION AREA').
        """
        if not name:
            return "MAIN SET"
        cleaned = re.sub(r'[\s/]+$', '', name.strip())
        cleaned = cleaned.strip(".:-–—/ ").upper()
        # Collapse multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned or "MAIN SET"

    @classmethod
    def canonicalize_location_name(cls, name: str, interior_exterior: str = "INT") -> str:
        """
        Resolves screenplay slugline variations, inversions, and sub-location aliases
        into unified canonical filming locations to eliminate duplicate cards.
        E.g.:
          - 'PROD H - ALLOCATED ROOM' & 'PROD H /ROOM ALLOCATED' & 'ALLOCATED ROOM' & 'ROOM ALLOCATED' -> 'PRODUCTION HOUSE - ALLOCATED ROOM'
          - 'PROD OFC / RECEPTION', 'RECEPTION AREA', 'PROD HOUSE/RECEPTION' -> 'PRODUCTION HOUSE - RECEPTION'
          - 'PROD ROOM/SRUJAN ROOM' & 'PROD ROOM/SRUJAN\'S ROOM' -> 'PRODUCTION HOUSE - SRUJAN\'S ROOM'
          - 'PRODUCTION HOUSE/PRODUCER ROOM', 'PROD ROOM/DOOR', 'PROD ROOM' -> 'PRODUCTION HOUSE - PRODUCER\'S ROOM'
          - 'PROD HOUSE , GATE/ROAD' -> 'PRODUCTION HOUSE - GATE / ROAD'
        """
        if not name:
            return "MAIN SET"

        cleaned = cls.sanitize_location_name(name)
        if not cleaned or cls.is_false_location(cleaned):
            return "MAIN SET"

        t = cleaned.upper()
        ie = (interior_exterior or "INT").upper()

        # 1. Detect Production House facility variations
        is_prod_complex = any(k in t for k in [
            "PROD H", "PROD HOUSE", "PRODUCTION HOUSE", "PROD OFC", 
            "PROD OFFICE", "PROD ROOM", "RECEPTION", "SRUJAN", "ALLOCATED"
        ])

        if is_prod_complex:
            # Gate / Road / Exterior
            if any(k in t for k in ["GATE", "ROAD", "DRIVEWAY", "STREET", "OUTSIDE"]) or "EXT" in ie:
                return "PRODUCTION HOUSE - GATE / ROAD"

            # Reception
            if "RECEPTION" in t:
                return "PRODUCTION HOUSE - RECEPTION"

            # Allocated Room (handles 'ROOM ALLOCATED', 'ALLOCATED ROOM', 'PROD H/ROOM', etc.)
            if "ALLOCATED" in t or t in {"PROD H/ROOM", "PROD HOUSE/ROOM", "PROD H - ROOM", "ROOM ALLOCATED", "ALLOCATED ROOM"}:
                return "PRODUCTION HOUSE - ALLOCATED ROOM"

            # Srujan's Room
            if "SRUJAN" in t:
                return "PRODUCTION HOUSE - SRUJAN'S ROOM"

            # Producer's Room / Executive Cabin / Main Prod Room
            if "PRODUCER" in t or any(p in t for p in ["PROD ROOM", "PROD ROOM/DOOR", "PRODUCER ROOM", "PROD CABIN"]):
                return "PRODUCTION HOUSE - PRODUCER'S ROOM"

            return "PRODUCTION HOUSE - MAIN FACILITY"

        # 2. General Screenplay Heuristics
        # Clean redundant sub-angle / area suffixes
        t = re.sub(r'\b(AREA|ZONE|CORNER|DOOR)\b', '', t).strip('.:-–—/ ')
        t = re.sub(r'\s+', ' ', t)

        # Inverted two-word rooms (e.g. 'ROOM ALLOCATED' -> 'ALLOCATED ROOM')
        words = t.split()
        if len(words) == 2 and 'ROOM' in words:
            other = [w for w in words if w != 'ROOM'][0]
            t = f"{other} ROOM"

        # Possessive standardization for names/titles
        person_titles = {"SRUJAN", "VASU", "VICKY", "KALYAN", "PRODUCER", "DIRECTOR", "WRITER", "CHIEF", "VANCE", "ELENA"}
        for p in person_titles:
            t = re.sub(rf"\b{p}\s+ROOM\b", f"{p}'S ROOM", t)

        # Standardize separator
        t = re.sub(r'\s*[/,]\s*', ' - ', t)
        t = re.sub(r'\s*-\s*', ' - ', t)

        return t or "MAIN SET"

    @classmethod
    def is_false_location(cls, name: str) -> bool:
        """
        Detects if a location name is actually a transition or false cut artifact
        (e.g., 'ER' from 'INT. ER-CUT', 'INTERCUT', 'CUT TO', etc.).
        """
        cleaned = cls.sanitize_location_name(name).upper()
        false_names = {
            "ER", "ER-CUT", "ERCUT", "INTERCUT", "INTER-CUT", "INTER CUT",
            "CUT", "CUT TO", "SMASH CUT", "DISSOLVE", "TRANSITION", "UNKNOWN",
            "UNKNOWN LOCATION"
        }
        return cleaned in false_names or "INTERCUT" in cleaned or "ER-CUT" in cleaned

    @classmethod
    def calculate_location_cost(
        cls,
        name: str,
        interior_exterior: str = "INT",
        day_night: str = "DAY",
        scene_count: int = 1,
        required_days: int = 1,
        company_move_required: bool = False
    ) -> float:
        """
        Calculates a realistic, dynamic estimated cost for a filming location based on:
        - Location tier and category (specialized vs public street vs executive office vs residential vs doorway)
        - Interior vs Exterior (exterior requires municipal permits, traffic control, police liaison)
        - Day vs Night (night shoots incur municipal night filming surcharges and quiet-hour permits)
        - Required shooting days (with multi-day volume scaling)
        - Scene count density (power, utility, and maintenance buffer)
        - Company move logistics fee
        - Deterministic variance to ensure unique, justifiable costs
        """
        name_upper = cls.sanitize_location_name(name).upper()
        ie_upper = (interior_exterior or "INT").upper()
        dn_upper = (day_night or "DAY").upper()
        days = max(1, required_days)
        scenes = max(1, scene_count)

        # 1. Base Daily Rate by Category Tier
        base_daily_rate = 4500.0  # Default base

        if any(kw in name_upper for kw in cls.TIER_KEYWORDS["SPECIALIZED"]):
            base_daily_rate = 14000.0
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["PUBLIC_EXTERIOR"]) or "EXT" in ie_upper:
            base_daily_rate = 10500.0
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["EXECUTIVE_COMMERCIAL"]):
            base_daily_rate = 7000.0
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["RESIDENTIAL"]):
            base_daily_rate = 5500.0
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["COMPACT_SECONDARY"]):
            base_daily_rate = 3500.0

        # Exterior baseline check
        if "EXT" in ie_upper and base_daily_rate < 8500.0:
            base_daily_rate = 8500.0

        # 2. Required Days Scaling (with multi-day discount after day 2)
        if days == 1:
            days_cost = base_daily_rate
        elif days == 2:
            days_cost = base_daily_rate * 2.0
        else:
            # 10% discount on days beyond 2
            days_cost = base_daily_rate * (2.0 + 0.9 * (days - 2))

        # 3. Day vs Night Surcharge (+25% for night filming permits and off-hours coordination)
        night_multiplier = 1.25 if "NIGHT" in dn_upper else 1.0
        cost = days_cost * night_multiplier

        # 4. Company Move Fee (+₹1,800 for unit parking, generator placement, load-in/out)
        if company_move_required:
            cost += 1800.0

        # 5. Scene Density / Wear & Tear Buffer (+₹600 per additional scene beyond 2)
        if scenes > 2:
            cost += (scenes - 2) * 600.0

        # 6. Deterministic Name Hash Offset (+/- ₹100 - ₹500 variance to ensure unique, realistic figures)
        name_hash = sum(ord(c) for c in name_upper)
        variance = ((name_hash % 9) - 4) * 120.0  # range -480 to +480
        cost += variance

        # Round to nearest ₹50
        final_cost = round(cost / 50.0) * 50.0
        return max(1500.0, float(final_cost))

    @classmethod
    def get_location_description(cls, name: str, interior_exterior: str = "INT") -> str:
        """Returns a descriptive classification for the location card."""
        name_upper = cls.sanitize_location_name(name).upper()
        ie = "Exterior" if "EXT" in (interior_exterior or "").upper() else "Interior"

        if any(kw in name_upper for kw in cls.TIER_KEYWORDS["SPECIALIZED"]):
            return f"{ie} Specialized Facility / Soundstage - {name}"
        if any(kw in name_upper for kw in cls.TIER_KEYWORDS["PUBLIC_EXTERIOR"]):
            return f"{ie} Public / Municipal Location - {name}"
        if any(kw in name_upper for kw in cls.TIER_KEYWORDS["EXECUTIVE_COMMERCIAL"]):
            return f"{ie} Commercial / Production Facility - {name}"
        if any(kw in name_upper for kw in cls.TIER_KEYWORDS["RESIDENTIAL"]):
            return f"{ie} Residential / Practical Location - {name}"
        return f"Studio Stage / Practical Location - {name}"

    @classmethod
    def generate_specifications(
        cls,
        name: str,
        interior_exterior: str = "INT",
        day_night: str = "DAY",
        estimated_cost: float = 5000.0
    ) -> Dict[str, str]:
        """
        Generates comprehensive, professional production specifications covering the 6 film-scouting criteria:
        1. Visuals and Space
        2. Natural Light
        3. Crew Facilities
        4. Budget and Availability
        5. Safety and Weather Backups
        6. Permits and Legal Rules
        """
        name_clean = cls.sanitize_location_name(name)
        name_upper = name_clean.upper()
        ie_upper = (interior_exterior or "INT").upper()
        dn_upper = (day_night or "DAY").upper()
        is_ext = "EXT" in ie_upper or any(kw in name_upper for kw in cls.TIER_KEYWORDS["PUBLIC_EXTERIOR"])
        is_night = any(k in dn_upper for k in ["NIGHT", "EVENING", "DUSK"])
        cost_str = f"₹{estimated_cost:,.0f}"

        if is_ext:
            return {
                "visuals_and_space": f"Expansive open-air depth ({name_clean}). Unobstructed spatial clearance for 50-foot camera cranes, tracking vehicles, wide establishing shots, and multi-actor dialogue blocks.",
                "natural_light": "High ambient solar exposure with direct zenith noon sunlight. Requires 12x12 overhead diffusion butterfly silks, silver/white bounce boards, and camera matte-box IRND filters to control harsh facial contrast.",
                "crew_facilities": "Curb-side and designated lane parking for 3 technical grip trucks, mobile honeywagon restrooms, generator basecamp zones, and pop-up cast/crew catering shade tents.",
                "budget_and_availability": f"Estimated site permit & location rental: {cost_str}/shoot day. Requires 10 business days municipal advance booking lead time and refundable ₹15,000 security/cleaning deposit.",
                "safety_and_weather_backups": "High-visibility safety vests, illuminated night marshaling wands, and traffic diversion cones. Weatherproof pop-up canopies on immediate standby with backup interior holding location in case of rain.",
                "permits_and_legal_rules": "City Film Commission street filming permit and traffic police liaison for Intermittent Traffic Control (ITC). Sound curfew strictly enforced after 10:00 PM; public liability insurance policy required."
            }
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["SPECIALIZED"]):
            return {
                "visuals_and_space": f"Acoustically treated specialized facility ({name_clean}) with high 14ft industrial ceiling clearance. Pre-installed overhead lighting grids, smooth flooring for Dana Dolly / track glides, and modern architectural aesthetics.",
                "natural_light": "Fully light-controlled environment with high-grade optical baffles. Zero unwanted solar contamination, enabling instant switching between high-key sterile daylight and deep moody dramatic night lighting.",
                "crew_facilities": "High-capacity loading dock with freight elevator access, cast holding suite with private makeup mirror stations, 4 dedicated restrooms, and dual 3-phase 63A camlock power distro tie-ins.",
                "budget_and_availability": f"Commercial stage facility day rate: {cost_str}/day. Strict 12-hour portal-to-portal booking with 7-day advance reservation; overtime billed at ₹3,500/hr.",
                "safety_and_weather_backups": "100% climate-controlled HVAC indoor facility immune to weather conditions. Equipped with industrial CO2 fire suppression system, marked fire lanes, emergency battery lighting, and compliant eye-wash stations.",
                "permits_and_legal_rules": "Private commercial location agreement with property management. Facility environmental clearance, safety officer sign-off, and $1,000,000 general third-party liability insurance binder required."
            }
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["EXECUTIVE_COMMERCIAL"]):
            return {
                "visuals_and_space": f"Executive commercial production environment ({name_clean}) with 10-12ft acoustic drop-ceiling. Features executive desks, leather seating, and clean horizontal depth for over-the-shoulder conversation angles and slider moves.",
                "natural_light": "Floor-to-ceiling windows providing ample ambient daylight. Window neutral density (ND.6/ND.9) gel sheeting required during morning hours to match interior skin tones with exterior skyline exposure." if not is_night else "Total exterior blackout achieved via duvetyne window flags. Dimmable warm tungsten desk lamps and practical accent lighting establish high-contrast night executive mood.",
                "crew_facilities": "Dedicated green room for actor prep, executive boardroom serving as production office, high-speed Wi-Fi, 2 interior executive restrooms, and commercial 32A wall power outlets across perimeter.",
                "budget_and_availability": f"Executive commercial rental fee: {cost_str}/day. Weekend shoots preferred to prevent corporate disruption; 5-day advance booking notice with security deposit.",
                "safety_and_weather_backups": "Weatherproof enclosed facility with central air-conditioning. Building fire alarm bypass protocol scheduled with security; clearly illuminated emergency stairwell access.",
                "permits_and_legal_rules": "Commercial building management filming agreement, security badge clearance for all cast and crew members, noise curfew restrictions after 9:00 PM on weekdays."
            }
        elif any(kw in name_upper for kw in cls.TIER_KEYWORDS["RESIDENTIAL"]):
            return {
                "visuals_and_space": f"Authentic residential practical set ({name_clean}). Intimate domestic spatial layout ideal for handheld camera work, medium close-ups, and naturalistic actor staging across living/dining areas.",
                "natural_light": "Domestic window daylight varying throughout morning and afternoon. Requires lightweight beadboards and compact bi-color LED panels (Aputure 300c) to supplement interior light levels without bulky stands." if not is_night else "Cozy interior tungsten illumination. Practical household lamps on dimmer packs create rich domestic night warmth with deep natural shadows.",
                "crew_facilities": "Residential driveway parking for 1 essential equipment van (crew carpooling required), master bedroom utilized as talent green room, 1 domestic restroom, and standard 16A domestic circuit breakers.",
                "budget_and_availability": f"Residential location fee: {cost_str}/day. Direct homeowner agreement with flexible scheduling; 3-day advance notice required with 20% security deposit for property protection.",
                "safety_and_weather_backups": "Weatherproof indoor home setting. Heavy floor runners (layout board / Neoprene) laid throughout all high-traffic areas to safeguard flooring against tripods and equipment cases.",
                "permits_and_legal_rules": "Neighborhood association filming courtesy notification, residential street parking permits, and municipal quiet-hours adherence from 10:00 PM to 7:00 AM."
            }
        else:
            return {
                "visuals_and_space": f"Versatile practical interior setting ({name_clean}). Compact spatial configuration suitable for close-quarters framing, low-angle hi-hat shots, desk rigging, and tight two-character dialogue exchanges.",
                "natural_light": "Controlled interior ambient light supplemented with directional soft LED panels. Neutral density window treatment applied if exterior windows are in frame." if not is_night else "Artificial practical lighting with Astera tube edge lights. Zero daylight contamination, allowing cinematic shadow sculpting.",
                "crew_facilities": "Adjacent staging hallway for grip cases and battery charging, shared restroom facilities, dedicated sound isolation blankets to minimize hallway acoustic echo, and 20A AC wall power.",
                "budget_and_availability": f"Location day rate: {cost_str}/day. Flexible booking availability with 48-hour confirmation; standard 10-hour shoot day.",
                "safety_and_weather_backups": "Fully protected indoor environment unaffected by outdoor precipitation. Multi-class fire extinguishers on stand and clear egress pathways maintained across doorways.",
                "permits_and_legal_rules": "Location release agreement signed by authorized facility representative. Standard film production insurance and safety guidelines enforced."
            }

