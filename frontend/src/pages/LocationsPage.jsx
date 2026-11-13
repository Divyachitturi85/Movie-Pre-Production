import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  MapPin,
  Search,
  AlertCircle,
  DollarSign,
  Calendar,
  Layers,
  Sun,
  Truck,
  ShieldCheck,
  FileText,
  Maximize2,
  Info,
  X,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { analysisService } from '../services/api';

function getLocationSpecs(loc) {
  if (loc.specifications && Object.keys(loc.specifications).length >= 6) {
    return loc.specifications;
  }
  const name = loc.name || 'Main Location';
  const nameUp = name.toUpperCase();
  const ie = (loc.interior_exterior || 'INT').toUpperCase();
  const dn = (loc.day_night || 'DAY').toUpperCase();
  const isExt = ie.includes('EXT') || nameUp.includes('ROAD') || nameUp.includes('GATE') || nameUp.includes('OUTSIDE') || nameUp.includes('STREET');
  const isNight = dn.includes('NIGHT') || dn.includes('EVENING') || dn.includes('DUSK');
  const cost = loc.estimated_cost || 5000;
  const costStr = `₹${cost.toLocaleString('en-IN')}`;

  if (isExt) {
    return {
      visuals_and_space: `Expansive open-air depth for ${name}. Unobstructed spatial clearance for 50ft camera cranes, vehicle mounts, tracking shots, and wide establishing coverage.`,
      natural_light: `Direct overhead solar exposure with high ambient contrast. Requires 12x12 overhead diffusion butterfly silks, silver/white bounce boards, and camera IRND filters for exposure control.`,
      crew_facilities: `Curb-side and designated lane parking for 3 technical grip trucks, mobile honeywagon restrooms, generator basecamp zones, and pop-up catering shade tents.`,
      budget_and_availability: `Estimated site permit & location rental: ${costStr}/shoot day. Requires 10 business days municipal advance booking lead time and refundable ₹15,000 security/cleaning deposit.`,
      safety_and_weather_backups: `High-visibility safety vests, illuminated night marshaling wands, and traffic diversion cones. Weatherproof pop-up canopies on immediate standby with backup interior holding location in case of rain.`,
      permits_and_legal_rules: `City Film Commission street filming permit and traffic police liaison for Intermittent Traffic Control (ITC). Sound curfew strictly enforced after 10:00 PM; public liability insurance policy required.`
    };
  } else if (nameUp.includes('LAB') || nameUp.includes('HOSPITAL') || nameUp.includes('STUDIO')) {
    return {
      visuals_and_space: `Acoustically treated specialized facility (${name}) with 14ft industrial ceiling clearance. Pre-installed overhead lighting grids, smooth flooring for Dana Dolly / track glides, and modern architectural aesthetics.`,
      natural_light: `Fully light-controlled environment with optical baffles. Zero unwanted solar contamination, enabling instant switching between high-key sterile daylight and deep moody dramatic night lighting.`,
      crew_facilities: `High-capacity loading dock with freight elevator access, cast holding suite with private makeup mirror stations, 4 dedicated restrooms, and dual 3-phase 63A camlock power distro tie-ins.`,
      budget_and_availability: `Commercial stage facility day rate: ${costStr}/day. Strict 12-hour portal-to-portal booking with 7-day advance reservation; overtime billed at ₹3,500/hr.`,
      safety_and_weather_backups: `100% climate-controlled HVAC indoor facility immune to weather conditions. Equipped with industrial CO2 fire suppression system, marked fire lanes, emergency battery lighting, and compliant eye-wash stations.`,
      permits_and_legal_rules: `Private commercial location agreement with property management. Facility environmental clearance, safety officer sign-off, and ₹1,000,000 general third-party liability insurance binder required.`
    };
  } else if (nameUp.includes('PRODUCER') || nameUp.includes('OFFICE') || nameUp.includes('PROD')) {
    return {
      visuals_and_space: `Executive commercial production environment (${name}) with 10-12ft acoustic drop-ceiling. Features executive desks, leather seating, and clean horizontal depth for over-the-shoulder conversation angles and slider moves.`,
      natural_light: !isNight
        ? `Floor-to-ceiling windows providing ample ambient daylight. Window neutral density (ND.6/ND.9) gel sheeting required during morning hours to match interior skin tones with exterior skyline exposure.`
        : `Total exterior blackout achieved via duvetyne window flags. Dimmable warm tungsten desk lamps and practical accent lighting establish high-contrast night executive mood.`,
      crew_facilities: `Dedicated green room for actor prep, executive boardroom serving as production office, high-speed Wi-Fi, 2 interior executive restrooms, and commercial 32A wall power outlets across perimeter.`,
      budget_and_availability: `Executive commercial rental fee: ${costStr}/day. Weekend shoots preferred to prevent corporate disruption; 5-day advance booking notice with security deposit.`,
      safety_and_weather_backups: `Weatherproof enclosed facility with central air-conditioning. Building fire alarm bypass protocol scheduled with security; clearly illuminated emergency stairwell access.`,
      permits_and_legal_rules: `Commercial building management filming agreement, security badge clearance for all cast and crew members, noise curfew restrictions after 9:00 PM on weekdays.`
    };
  } else if (nameUp.includes('HOUSE') || nameUp.includes('HOME') || nameUp.includes('APARTMENT') || nameUp.includes('ROOM')) {
    return {
      visuals_and_space: `Authentic residential/practical room layout (${name}). Intimate spatial geometry ideal for handheld camera work, medium close-ups, and naturalistic actor staging across furniture pieces.`,
      natural_light: !isNight
        ? `Domestic window daylight varying throughout morning and afternoon. Requires lightweight beadboards and compact bi-color LED panels (Aputure 300c) to supplement interior light levels without bulky stands.`
        : `Cozy interior tungsten illumination. Practical household lamps on dimmer packs create rich domestic night warmth with deep natural shadows.`,
      crew_facilities: `Driveway and lane parking for 1 essential equipment van, quiet master bedroom utilized as talent green room, domestic restroom, and standard circuit breaker protection.`,
      budget_and_availability: `Practical location fee: ${costStr}/day. Direct owner agreement with flexible scheduling; 3-day advance notice required with security deposit for property protection.`,
      safety_and_weather_backups: `Weatherproof indoor setting. Heavy floor layout boards / Neoprene runners laid throughout all high-traffic areas to safeguard flooring against tripods and equipment cases.`,
      permits_and_legal_rules: `Property filming release agreement, neighbor courtesy notification, and local municipal quiet-hours adherence from 10:00 PM to 7:00 AM.`
    };
  } else {
    return {
      visuals_and_space: `Versatile practical interior setting (${name}). Compact spatial configuration suitable for close-quarters framing, low-angle hi-hat shots, desk rigging, and tight two-character dialogue exchanges.`,
      natural_light: !isNight
        ? `Controlled interior ambient light supplemented with directional soft LED panels. Neutral density window treatment applied if exterior windows are in frame.`
        : `Artificial practical lighting with Astera tube edge lights. Zero daylight contamination, allowing cinematic shadow sculpting.`,
      crew_facilities: `Adjacent staging hallway for grip cases and battery charging, shared restroom facilities, dedicated sound isolation blankets to minimize hallway acoustic echo, and 20A AC wall power.`,
      budget_and_availability: `Location day rate: ${costStr}/day. Flexible booking availability with 48-hour confirmation; standard 10-hour shoot day.`,
      safety_and_weather_backups: `Fully protected indoor environment unaffected by outdoor precipitation. Multi-class fire extinguishers on stand and clear egress pathways maintained across doorways.`,
      permits_and_legal_rules: `Location release agreement signed by authorized facility representative. Standard film production insurance and safety guidelines enforced.`
    };
  }
}

export default function LocationsPage() {
  const { currentProject } = useOutletContext();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeModalLoc, setActiveModalLoc] = useState(null);
  const [hoveredLocId, setHoveredLocId] = useState(null);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadLocations();
  }, [currentProject?.id]);

  const loadLocations = async () => {
    setLoading(true);
    try {
      const data = await analysisService.getLocations(currentProject.id);
      // Ensure clean canonical deduplication
      const deduplicated = deduplicateLocations(data || []);
      setLocations(deduplicated);
    } catch (err) {
      console.error('Failed to load locations:', err);
    } finally {
      setLoading(false);
    }
  };

  function deduplicateLocations(locList) {
    const map = new Map();
    for (const loc of locList) {
      const raw = (loc.name || '').toUpperCase().trim();
      let key = loc.name;
      if (raw.includes('RECEPTION')) {
        key = 'PRODUCTION HOUSE - RECEPTION';
      } else if (raw.includes('ALLOCATED') || raw === 'PROD H/ROOM' || raw === 'ROOM ALLOCATED' || raw === 'ALLOCATED ROOM') {
        key = 'PRODUCTION HOUSE - ALLOCATED ROOM';
      } else if (raw.includes('SRUJAN')) {
        key = "PRODUCTION HOUSE - SRUJAN'S ROOM";
      } else if (raw.includes('PRODUCER') || raw === 'PROD ROOM' || raw === 'PROD ROOM/DOOR') {
        key = "PRODUCTION HOUSE - PRODUCER'S ROOM";
      } else if (raw.includes('GATE') || raw.includes('ROAD')) {
        key = 'PRODUCTION HOUSE - GATE / ROAD';
      }

      if (!map.has(key)) {
        map.set(key, {
          ...loc,
          name: key,
          scene_ids: new Set(loc.scene_ids || [])
        });
      } else {
        const existing = map.get(key);
        (loc.scene_ids || []).forEach(s => existing.scene_ids.add(s));
        existing.scene_count = existing.scene_ids.size;
        existing.required_days = Math.max(1, Math.ceil((existing.scene_count + 1) / 3));
        existing.estimated_cost = Math.max(existing.estimated_cost || 0, loc.estimated_cost || 0);
      }
    }

    return Array.from(map.values()).map(l => ({
      ...l,
      scene_ids: Array.from(l.scene_ids).sort((a, b) => a - b)
    }));
  }

  const filtered = locations.filter(l =>
    l.name.toLowerCase().includes(search.toLowerCase()) ||
    l.interior_exterior.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="border-b border-[#27354F] pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <MapPin className="w-6 h-6 text-emerald-400" />
            <span>Locations & Set Requirements</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Sets, interior/exterior grouping, company move logistics, and scouting specifications.
          </p>
        </div>

        {/* Info Legend Banner */}
        <div className="flex items-center gap-2 text-[11px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-3 py-1.5 rounded-xl">
          <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Hover over any location card to flip it and view all 6 features! Click card to open full modal.</span>
        </div>
      </div>

      {/* Search */}
      <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex items-center gap-3">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search location by name or INT/EXT..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none flex-1"
        />
        <span className="text-[11px] text-slate-400 font-mono">
          Showing {filtered.length} locations
        </span>
      </div>

      {/* Grid of Locations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((loc) => {
          const specs = getLocationSpecs(loc);
          const isHovered = hoveredLocId === loc.id;

          return (
            <div
              key={loc.id}
              className="perspective-1000 h-[430px] w-full"
              onMouseEnter={() => setHoveredLocId(loc.id)}
              onMouseLeave={() => setHoveredLocId(null)}
            >
              <div
                className={`relative w-full h-full transition-transform duration-700 transform-style-3d cursor-pointer ${
                  isHovered ? 'rotate-y-180' : ''
                }`}
                onClick={() => setActiveModalLoc(loc)}
              >
                {/* FRONT FACE OF CARD */}
                <div className="absolute inset-0 w-full h-full backface-hidden bg-[#131B2A] border border-[#27354F] hover:border-emerald-500/60 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-slate-800 text-slate-300 font-mono border border-slate-700">
                        {loc.interior_exterior} • {loc.day_night}
                      </span>
                      {loc.company_move_required && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full">
                          <AlertCircle className="w-3 h-3" />
                          <span>Company Move</span>
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-bold text-white mb-1 group-hover:text-emerald-300 transition-colors line-clamp-2">
                      {loc.name}
                    </h3>
                    <p className="text-xs text-slate-400 mb-4 line-clamp-1">
                      {loc.address_or_description || 'Stage / Practical Location'}
                    </p>

                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div className="bg-[#182235] p-2.5 rounded-xl border border-[#222E42]">
                        <span className="text-[11px] text-slate-400 block">Total Scenes</span>
                        <span className="font-bold text-white text-sm">{loc.scene_count} Scenes</span>
                      </div>
                      <div className="bg-[#182235] p-2.5 rounded-xl border border-[#222E42]">
                        <span className="text-[11px] text-slate-400 block">Required Shoot</span>
                        <span className="font-bold text-emerald-400 text-sm">{loc.required_days} Days</span>
                      </div>
                    </div>

                    {/* Quick highlights */}
                    <div className="space-y-2 text-[11px] text-slate-300 pt-2 border-t border-[#222E42]/80">
                      <div className="flex items-start gap-1.5 text-slate-400">
                        <Maximize2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        <span className="line-clamp-2"><strong className="text-slate-200">Space:</strong> {specs.visuals_and_space}</span>
                      </div>
                      <div className="flex items-start gap-1.5 text-slate-400">
                        <Sun className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <span className="line-clamp-1"><strong className="text-slate-200">Light:</strong> {specs.natural_light}</span>
                      </div>
                    </div>
                  </div>

                  {/* Front Card Footer */}
                  <div className="pt-3 mt-2 border-t border-[#222E42] flex items-center justify-between text-xs">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase tracking-wider font-semibold">Est. Site Cost</span>
                      <span className="font-bold text-amber-400 font-mono text-sm">
                        ₹{(loc.estimated_cost || 1500).toLocaleString('en-IN')}
                      </span>
                    </div>

                    <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/30">
                      <span>Hover to Flip</span>
                      <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                    </span>
                  </div>
                </div>

                {/* BACK FACE OF CARD (FLIPPED ON HOVER - SHOWS 6 FEATURES) */}
                <div className="absolute inset-0 w-full h-full backface-hidden rotate-y-180 bg-[#0F1622] border-2 border-emerald-500/70 rounded-2xl p-4 shadow-2xl flex flex-col justify-between overflow-hidden">
                  <div className="flex items-center justify-between border-b border-[#222E42] pb-2 mb-2">
                    <div className="min-w-0 pr-2">
                      <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-400 block">
                        6 Location Features
                      </span>
                      <h4 className="text-xs font-bold text-white truncate">{loc.name}</h4>
                    </div>
                    <span className="text-[9px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700 shrink-0">
                      Click for Modal
                    </span>
                  </div>

                  {/* 6 Features Scrollable List */}
                  <div className="flex-1 overflow-y-auto space-y-2 pr-1 text-[11px]">
                    {/* 1. Visuals and Space */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-cyan-500/20">
                      <span className="font-bold text-cyan-300 flex items-center gap-1 text-[10.5px]">
                        <Maximize2 className="w-3 h-3 text-cyan-400 shrink-0" />
                        <span>1. Visuals & Space</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.visuals_and_space}</p>
                    </div>

                    {/* 2. Natural Light */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-amber-500/20">
                      <span className="font-bold text-amber-300 flex items-center gap-1 text-[10.5px]">
                        <Sun className="w-3 h-3 text-amber-400 shrink-0" />
                        <span>2. Natural Light</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.natural_light}</p>
                    </div>

                    {/* 3. Crew Facilities */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-emerald-500/20">
                      <span className="font-bold text-emerald-300 flex items-center gap-1 text-[10.5px]">
                        <Truck className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>3. Crew Facilities</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.crew_facilities}</p>
                    </div>

                    {/* 4. Budget and Availability */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-yellow-500/20">
                      <span className="font-bold text-yellow-300 flex items-center gap-1 text-[10.5px]">
                        <DollarSign className="w-3 h-3 text-yellow-400 shrink-0" />
                        <span>4. Budget & Availability</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.budget_and_availability}</p>
                    </div>

                    {/* 5. Safety and Weather Backups */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-rose-500/20">
                      <span className="font-bold text-rose-300 flex items-center gap-1 text-[10.5px]">
                        <ShieldCheck className="w-3 h-3 text-rose-400 shrink-0" />
                        <span>5. Safety & Weather Backups</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.safety_and_weather_backups}</p>
                    </div>

                    {/* 6. Permits and Legal Rules */}
                    <div className="bg-[#141E2F] p-2 rounded-lg border border-purple-500/20">
                      <span className="font-bold text-purple-300 flex items-center gap-1 text-[10.5px]">
                        <FileText className="w-3 h-3 text-purple-400 shrink-0" />
                        <span>6. Permits & Legal Rules</span>
                      </span>
                      <p className="text-slate-300 text-[10px] leading-relaxed mt-0.5">{specs.permits_and_legal_rules}</p>
                    </div>
                  </div>

                  {/* Back Card Footer */}
                  <div className="pt-2 mt-1 border-t border-[#222E42] flex items-center justify-between text-[10px]">
                    <span className="text-amber-400 font-bold font-mono">
                      Rate: ₹{(loc.estimated_cost || 1500).toLocaleString('en-IN')}/day
                    </span>
                    <span className="text-slate-400 italic">Hover off to flip ↩</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Detailed Modal Dialog (Opens on card click or tap) */}
      {activeModalLoc && (() => {
        const specs = getLocationSpecs(activeModalLoc);
        return (
          <div
            className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setActiveModalLoc(null)}
          >
            <div
              className="bg-[#131B2A] border border-emerald-500/50 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between border-b border-[#27354F] pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">
                      {activeModalLoc.interior_exterior} • {activeModalLoc.day_night}
                    </span>
                    {activeModalLoc.company_move_required && (
                      <span className="flex items-center gap-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full">
                        <AlertCircle className="w-3 h-3" />
                        <span>Company Move Required</span>
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl font-bold text-white">{activeModalLoc.name}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {activeModalLoc.address_or_description || 'Stage / Practical Location'}
                  </p>
                </div>

                <button
                  onClick={() => setActiveModalLoc(null)}
                  className="p-1.5 rounded-lg bg-[#182235] text-slate-400 hover:text-white border border-[#27354F] transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Quick Numbers Bar */}
              <div className="grid grid-cols-3 gap-3 text-xs">
                <div className="bg-[#182235] p-3 rounded-xl border border-[#222E42]">
                  <span className="text-[11px] text-slate-400 block">Total Scenes</span>
                  <span className="font-bold text-white text-base">{activeModalLoc.scene_count}</span>
                </div>
                <div className="bg-[#182235] p-3 rounded-xl border border-[#222E42]">
                  <span className="text-[11px] text-slate-400 block">Required Days</span>
                  <span className="font-bold text-emerald-400 text-base">{activeModalLoc.required_days} Days</span>
                </div>
                <div className="bg-[#182235] p-3 rounded-xl border border-[#222E42]">
                  <span className="text-[11px] text-slate-400 block">Est. Location Cost</span>
                  <span className="font-bold text-amber-400 font-mono text-base">
                    ₹{(activeModalLoc.estimated_cost || 1500).toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              {/* 6 Structured Scouting Criteria Sections */}
              <div className="space-y-4 pt-1">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Production Scouting & Facility Criteria</span>
                </h3>

                <div className="space-y-3">
                  {/* 1. Visuals and Space */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
                      <Maximize2 className="w-4 h-4 text-cyan-400" />
                      <span>1. Visuals and Space</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.visuals_and_space}
                    </p>
                  </div>

                  {/* 2. Natural Light */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                      <Sun className="w-4 h-4 text-amber-400" />
                      <span>2. Natural Light</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.natural_light}
                    </p>
                  </div>

                  {/* 3. Crew Facilities */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                      <Truck className="w-4 h-4 text-emerald-400" />
                      <span>3. Crew Facilities</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.crew_facilities}
                    </p>
                  </div>

                  {/* 4. Budget and Availability */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-yellow-300 flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4 text-yellow-400" />
                      <span>4. Budget and Availability</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.budget_and_availability}
                    </p>
                  </div>

                  {/* 5. Safety and Weather Backups */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-rose-400" />
                      <span>5. Safety and Weather Backups</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.safety_and_weather_backups}
                    </p>
                  </div>

                  {/* 6. Permits and Legal Rules */}
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42] space-y-1">
                    <span className="text-xs font-bold text-purple-300 flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-purple-400" />
                      <span>6. Permits and Legal Rules</span>
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed pl-5.5">
                      {specs.permits_and_legal_rules}
                    </p>
                  </div>
                </div>
              </div>

              {/* Close Button */}
              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => setActiveModalLoc(null)}
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-5 py-2 rounded-xl text-xs transition"
                >
                  Close Details
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
