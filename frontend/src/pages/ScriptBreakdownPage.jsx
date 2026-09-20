import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import {
  Layers,
  Search,
  Filter,
  Users,
  Package,
  Sparkles,
  Zap,
  Car,
  ShieldAlert,
  Camera,
  Clock,
  Plus,
  Tag,
  AlertCircle
} from 'lucide-react';
import { analysisService } from '../services/api';

const CATEGORY_COLORS = {
  PROP: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  COSTUME: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  VEHICLE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  EQUIPMENT: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  VFX: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  SFX: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  WEAPON: 'bg-red-500/10 text-red-400 border-red-500/30',
  ANIMAL: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
};

export default function ScriptBreakdownPage() {
  const { currentProject } = useOutletContext();
  const navigate = useNavigate();

  const [scenes, setScenes] = useState([]);
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [complexityFilter, setComplexityFilter] = useState('ALL');

  useEffect(() => {
    if (!currentProject?.id) return;
    loadBreakdownData();
  }, [currentProject?.id]);

  const loadBreakdownData = async () => {
    setLoading(true);
    try {
      const [scData, elData] = await Promise.all([
        analysisService.getScenes(currentProject.id).catch(() => []),
        analysisService.getElements(currentProject.id).catch(() => [])
      ]);
      setScenes(scData);
      setElements(elData);
    } catch (err) {
      console.error('Failed to load breakdown:', err);
    } finally {
      setLoading(false);
    }
  };

  // Map elements by scene_id
  const elementsByScene = {};
  elements.forEach(el => {
    if (el.scene_id) {
      elementsByScene[el.scene_id] = elementsByScene[el.scene_id] || [];
      elementsByScene[el.scene_id].push(el);
    }
  });

  const filteredScenes = scenes.filter(sc => {
    const matchesSearch =
      (sc.heading || '').toLowerCase().includes(search.toLowerCase()) ||
      (sc.location_name || '').toLowerCase().includes(search.toLowerCase());
    const matchesComplexity =
      complexityFilter === 'ALL' || sc.complexity_level === complexityFilter;
    return matchesSearch && matchesComplexity;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              StudioBinder-Inspired Workflow
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Scene-by-Scene Script Breakdown Sheets
          </h1>
          <p className="text-xs text-slate-400">
            Categorized production elements, cast requirements, and complexity factors extracted via NLP.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/elements')}
            className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-200 border border-[#27354F] px-4 py-2 rounded-xl text-xs font-semibold transition"
          >
            <Package className="w-3.5 h-3.5 text-amber-400" />
            <span>View All Assets ({elements.length})</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter by scene heading, set, or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={complexityFilter}
            onChange={(e) => setComplexityFilter(e.target.value)}
            className="bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500"
          >
            <option value="ALL">All Complexity Levels</option>
            <option value="LOW">Low Complexity</option>
            <option value="MEDIUM">Medium Complexity</option>
            <option value="HIGH">High Complexity</option>
            <option value="VERY HIGH">Very High Complexity</option>
          </select>
        </div>
      </div>

      {/* Breakdown Cards Grid */}
      {filteredScenes.length === 0 ? (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center text-xs text-slate-400">
          No breakdown scenes match your filter criteria.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredScenes.map((sc) => {
            const scElements = elementsByScene[sc.id] || [];
            return (
              <div
                key={sc.id}
                className="bg-[#131B2A] border border-[#27354F] hover:border-slate-600 rounded-2xl p-5 sm:p-6 shadow-md transition"
              >
                {/* Scene Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#222E42] pb-3 mb-4">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-black text-xs">
                      SCENE {sc.scene_number}
                    </span>
                    <h3 className="font-bold text-sm text-white">{sc.heading}</h3>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono text-[11px]">
                      {sc.interior_exterior} • {sc.time_of_day}
                    </span>
                    <span className="text-slate-400 font-mono">
                      {sc.estimated_pages} pgs ({sc.estimated_duration_minutes}m shoot)
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                      sc.complexity_level === 'HIGH' || sc.complexity_level === 'VERY HIGH'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : sc.complexity_level === 'MEDIUM'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    }`}>
                      {sc.complexity_level} Complexity ({sc.complexity_score}/10)
                    </span>
                  </div>
                </div>

                {/* Grid of Production Elements */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4 text-xs">
                  {/* Action Excerpt */}
                  <div className="md:col-span-5 bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                      Screenplay Context
                    </div>
                    <p className="font-screenplay text-[11px] text-slate-300 leading-relaxed max-h-32 overflow-y-auto whitespace-pre-wrap">
                      {sc.action_text || sc.raw_content || 'No action description.'}
                    </p>
                  </div>

                  {/* Production Elements Pill Badges */}
                  <div className="md:col-span-7 space-y-3">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      Extracted Production Elements ({scElements.length})
                    </div>

                    {scElements.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {scElements.map((el, i) => {
                          const badgeColor = CATEGORY_COLORS[el.category] || 'bg-slate-800 text-slate-300 border-slate-700';
                          return (
                            <span
                              key={i}
                              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${badgeColor}`}
                              title={`${el.category}: ${el.description || el.name} (Source: ${el.extraction_source})`}
                            >
                              <span className="font-bold opacity-75 text-[10px]">{el.category}:</span>
                              <span>{el.name}</span>
                              <span className="text-[10px] opacity-60 font-mono">
                                {Math.round((el.confidence || 0.85) * 100)}%
                              </span>
                            </span>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No special production assets tagged.</p>
                    )}

                    {/* Complexity Factors Tags */}
                    {sc.complexity_factors && (
                      <div className="pt-2 border-t border-[#222E42] text-[11px] text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
                        {Object.entries(sc.complexity_factors).map(([k, v], idx) => (
                          <span key={idx} className="flex items-center gap-1">
                            <span className="text-slate-500">•</span>
                            <span>{typeof v === 'string' ? v : JSON.stringify(v)}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
