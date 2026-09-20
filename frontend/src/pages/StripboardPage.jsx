import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  FileSpreadsheet,
  Search,
  Filter,
  Download,
  Calendar,
  Layers,
  Sparkles
} from 'lucide-react';
import { scheduleService } from '../services/api';

export default function StripboardPage() {
  const { currentProject } = useOutletContext();
  const [strips, setStrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dayFilter, setDayFilter] = useState('ALL');
  const [ieFilter, setIeFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!currentProject?.id) return;
    loadStripboard();
  }, [currentProject?.id]);

  const loadStripboard = async () => {
    setLoading(true);
    try {
      const data = await scheduleService.getStripboard(currentProject.id);
      setStrips(data.strips || []);
    } catch (err) {
      console.error('Failed to load stripboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const uniqueDays = Array.from(new Set(strips.map(s => s.shooting_day))).sort((a,b) => a - b);

  const filtered = strips.filter(s => {
    const matchesSearch =
      (s.heading || '').toLowerCase().includes(search.toLowerCase()) ||
      (s.location_name || '').toLowerCase().includes(search.toLowerCase());
    const matchesDay = dayFilter === 'ALL' || s.shooting_day === parseInt(dayFilter);
    const matchesIe = ieFilter === 'ALL' || s.interior_exterior === ieFilter;
    return matchesSearch && matchesDay && matchesIe;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              Movie Magic Scheduling-Compatible
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Production Stripboard
          </h1>
          <p className="text-xs text-slate-400">
            Industry color-coded stripboard layout for physical production scheduling.
          </p>
        </div>

        {/* Color Legend */}
        <div className="flex flex-wrap items-center gap-3 text-[11px] font-semibold bg-[#131B2A] border border-[#27354F] px-3.5 py-2 rounded-xl">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#FEF08A] border border-amber-400"></span>
            <span className="text-slate-300">EXT. DAY</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#FFFFFF] border border-slate-300"></span>
            <span className="text-slate-300">INT. DAY</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#BBF7D0] border border-emerald-400"></span>
            <span className="text-slate-300">EXT. NIGHT</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#BFDBFE] border border-blue-400"></span>
            <span className="text-slate-300">INT. NIGHT</span>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search scene # or set..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>

        <div>
          <select
            value={dayFilter}
            onChange={(e) => setDayFilter(e.target.value)}
            className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500"
          >
            <option value="ALL">All Shoot Days</option>
            {uniqueDays.map(d => (
              <option key={d} value={d}>Shoot Day {d}</option>
            ))}
          </select>
        </div>

        <div>
          <select
            value={ieFilter}
            onChange={(e) => setIeFilter(e.target.value)}
            className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500"
          >
            <option value="ALL">All Environments (INT & EXT)</option>
            <option value="INT">Interior (INT) Only</option>
            <option value="EXT">Exterior (EXT) Only</option>
          </select>
        </div>
      </div>

      {/* Stripboard Container */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-4 sm:p-6 shadow-xl space-y-2">
        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex justify-between">
          <span>Stripboard Strips ({filtered.length})</span>
          <span>Standard Color-Coded Physical Representation</span>
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">No strips found matching criteria</div>
        ) : (
          <div className="space-y-1.5">
            {filtered.map((strip, idx) => (
              <div
                key={idx}
                style={{ backgroundColor: strip.strip_color }}
                className="rounded-lg p-3 text-slate-950 font-sans shadow-sm flex flex-wrap items-center justify-between gap-3 border border-black/10 hover:brightness-95 transition"
              >
                {/* Left: Scene # & Heading */}
                <div className="flex items-center gap-3 min-w-[240px]">
                  <span className="w-12 h-7 bg-black/80 text-white font-black font-mono text-xs rounded flex items-center justify-center">
                    #{strip.scene_number}
                  </span>
                  <div>
                    <div className="font-extrabold text-xs tracking-tight uppercase truncate max-w-xs sm:max-w-md">
                      {strip.heading}
                    </div>
                    <div className="text-[11px] font-semibold opacity-75">
                      {strip.location_name}
                    </div>
                  </div>
                </div>

                {/* Center: Details */}
                <div className="flex items-center gap-4 text-xs font-semibold">
                  <span className="font-mono bg-black/10 px-2 py-0.5 rounded text-[11px]">
                    {strip.interior_exterior} • {strip.time_of_day}
                  </span>
                  <span className="font-mono text-[11px]">
                    {strip.estimated_pages} pgs
                  </span>
                  <span className="font-mono text-[11px]">
                    {strip.estimated_duration_minutes}m
                  </span>
                </div>

                {/* Right: Shoot Day badge & Complexity */}
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-black/15 text-slate-900 font-bold text-[10px] uppercase">
                    {strip.complexity_level}
                  </span>
                  <span className="px-3 py-1 rounded bg-black text-white font-mono font-bold text-xs">
                    DAY {strip.shooting_day}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
