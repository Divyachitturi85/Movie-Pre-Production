import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { MapPin, Search, AlertCircle, DollarSign, Calendar, Layers } from 'lucide-react';
import { analysisService } from '../services/api';

export default function LocationsPage() {
  const { currentProject } = useOutletContext();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!currentProject?.id) return;
    loadLocations();
  }, [currentProject?.id]);

  const loadLocations = async () => {
    setLoading(true);
    try {
      const data = await analysisService.getLocations(currentProject.id);
      setLocations(data);
    } catch (err) {
      console.error('Failed to load locations:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = locations.filter(l =>
    l.name.toLowerCase().includes(search.toLowerCase()) ||
    l.interior_exterior.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="border-b border-[#27354F] pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <MapPin className="w-6 h-6 text-emerald-400" />
          <span>Locations & Set Requirements</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Sets, interior/exterior grouping, company move flags, and estimated site permit costs.
        </p>
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
      </div>

      {/* Grid of Locations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((loc) => (
          <div
            key={loc.id}
            className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-5 shadow-md hover:border-slate-600 transition flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-800 text-slate-300 font-mono">
                  {loc.interior_exterior} • {loc.day_night}
                </span>
                {loc.company_move_required && (
                  <span className="flex items-center gap-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full">
                    <AlertCircle className="w-3 h-3" />
                    <span>Company Move</span>
                  </span>
                )}
              </div>

              <h3 className="text-base font-bold text-white mb-2">{loc.name}</h3>
              <p className="text-xs text-slate-400 mb-4">{loc.address_or_description || 'Stage / Practical Location'}</p>

              <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                <div className="bg-[#182235] p-2.5 rounded-xl border border-[#222E42]">
                  <span className="text-[11px] text-slate-400 block">Total Scenes</span>
                  <span className="font-bold text-white text-sm">{loc.scene_count}</span>
                </div>
                <div className="bg-[#182235] p-2.5 rounded-xl border border-[#222E42]">
                  <span className="text-[11px] text-slate-400 block">Required Days</span>
                  <span className="font-bold text-emerald-400 text-sm">{loc.required_days} days</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-[#222E42] flex items-center justify-between text-xs">
              <span className="text-slate-400">Est. Location Cost:</span>
              <span className="font-bold text-amber-400 font-mono">
                ₹{(loc.estimated_cost || 1500).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
