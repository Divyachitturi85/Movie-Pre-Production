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
  AlertCircle,
  RefreshCw,
  Sliders,
  CheckCircle2
} from 'lucide-react';
import { analysisService } from '../services/api';

const CATEGORY_COLORS = {
  PROP: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  COSTUME: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  VEHICLE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  EQUIPMENT: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
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
  const [reanalyzing, setReanalyzing] = useState(false);
  const [search, setSearch] = useState('');
  const [complexityFilter, setComplexityFilter] = useState('ALL');
  const [selectedCategoryTab, setSelectedCategoryTab] = useState('ALL'); // 'ALL', 'EQUIPMENT', 'PROPS'

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

  const handleReAnalyze = async () => {
    if (!currentProject?.id) return;
    setReanalyzing(true);
    try {
      await analysisService.runAnalysis(currentProject.id);
      await loadBreakdownData();
    } catch (err) {
      console.error('Re-analysis failed:', err);
      alert('Failed to re-run breakdown analysis.');
    } finally {
      setReanalyzing(false);
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
            Categorized production elements, camera/lighting shoot equipment, cast requirements, and complexity factors.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleReAnalyze}
            disabled={reanalyzing}
            className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 px-4 py-2 rounded-xl text-xs font-bold transition shadow-md disabled:opacity-50"
            title="Re-extract shoot equipment, props, and complexity for all scenes"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reanalyzing ? 'animate-spin' : ''}`} />
            <span>{reanalyzing ? 'Extracting Equipment & Assets...' : 'Re-Run Equipment Breakdown'}</span>
          </button>

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

          <select
            value={selectedCategoryTab}
            onChange={(e) => setSelectedCategoryTab(e.target.value)}
            className="bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">Show All Elements</option>
            <option value="EQUIPMENT">Equipment Only</option>
            <option value="PROPS">Props & Set Assets Only</option>
          </select>
        </div>
      </div>


      {/* Breakdown Cards Grid */}
      {loading ? (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center text-xs text-slate-400">
          <RefreshCw className="w-6 h-6 text-amber-400 animate-spin mx-auto mb-3" />
          Loading Script Breakdown Sheets & Equipment Packages...
        </div>
      ) : filteredScenes.length === 0 ? (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center text-xs text-slate-400">
          No breakdown scenes match your filter criteria.
        </div>
      ) : (
        <div className="space-y-5">
          {filteredScenes.map((sc) => {
            const scElements = elementsByScene[sc.id] || [];
            const equipmentItems = scElements.filter(e => e.category === 'EQUIPMENT');
            const propAndOtherItems = scElements.filter(e => e.category !== 'EQUIPMENT');

            const displayedEquipment = selectedCategoryTab === 'PROPS' ? [] : equipmentItems;
            const displayedProps = selectedCategoryTab === 'EQUIPMENT' ? [] : propAndOtherItems;
            const totalVisible = displayedEquipment.length + displayedProps.length;

            const isNightScene = (sc.time_of_day || '').toUpperCase().includes('NIGHT') || (sc.time_of_day || '').toUpperCase().includes('EVENING');

            return (
              <div
                key={sc.id}
                className="bg-[#131B2A] border border-[#27354F] hover:border-slate-600 rounded-2xl p-5 sm:p-6 shadow-md transition"
              >
                {/* Scene Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#222E42] pb-3 mb-4">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-black text-xs">
                      SCENE {sc.scene_number}
                    </span>
                    <h3 className="font-bold text-sm text-white">{sc.heading}</h3>

                    {/* Day vs Night Scene Shoot Indicator */}
                    {isNightScene ? (
                      <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold">
                        <span>🌙 Night Shoot Rig</span>
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[10px] font-bold">
                        <span>☀️ Day Shoot Rig</span>
                      </span>
                    )}
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
                <div className="grid grid-cols-1 md:grid-cols-12 gap-5 text-xs">
                  {/* Action Excerpt & Screenplay Context */}
                  <div className="md:col-span-4 bg-[#182235] p-4 rounded-xl border border-[#222E42] flex flex-col justify-between">
                    <div>
                      <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>Screenplay Context</span>
                        <span className="text-[10px] text-amber-400 font-mono">Scene {sc.scene_number}</span>
                      </div>
                      <p className="font-screenplay text-[11px] text-slate-300 leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap pr-1">
                        {sc.action_text || sc.raw_content || 'No action description.'}
                      </p>
                    </div>

                    {/* Complexity Factors Tags */}
                    {sc.complexity_factors && (
                      <div className="pt-3 mt-3 border-t border-[#222E42] text-[10px] text-slate-400 flex flex-wrap gap-x-3 gap-y-1">
                        {Object.entries(sc.complexity_factors).map(([k, v], idx) => (
                          <span key={idx} className="flex items-center gap-1">
                            <span className="text-slate-500">•</span>
                            <span>{typeof v === 'string' ? v : JSON.stringify(v)}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Production Elements & Equipment Section */}
                  <div className="md:col-span-8 space-y-4">
                    <div className="flex items-center justify-between border-b border-[#222E42] pb-2">
                      <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                        <span>Extracted Production Elements & Shoot Gear ({scElements.length})</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px]">
                        <span className="text-cyan-400 font-bold bg-cyan-950/60 border border-cyan-800/40 px-2 py-0.5 rounded">
                          {equipmentItems.length} Equipment Items
                        </span>
                        <span className="text-amber-400 font-bold bg-amber-950/60 border border-amber-800/40 px-2 py-0.5 rounded">
                          {propAndOtherItems.length} Props & Assets
                        </span>
                      </div>
                    </div>

                    {totalVisible === 0 ? (
                      <div className="p-4 bg-[#182235] rounded-xl border border-[#222E42] text-center text-xs text-slate-500 italic">
                        No special production assets tagged for this filter.
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {/* 1. Scene Props, Wardrobe & Physical Assets */}
                        {displayedProps.length > 0 && (
                          <div className="space-y-2">
                            <div className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                              <Package className="w-3.5 h-3.5 text-amber-400" />
                              <span>Scene Props & Assets ({displayedProps.length})</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {displayedProps.map((el, i) => {
                                const badgeColor = CATEGORY_COLORS[el.category] || 'bg-slate-800 text-slate-300 border-slate-700';
                                const confidencePct = Math.round((el.confidence || 0.85) * 100);
                                return (
                                  <span
                                    key={i}
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${badgeColor} transition hover:scale-102`}
                                    title={`${el.category}: ${el.description || el.name}\nAI Extraction Confidence: ${confidencePct}% certainty from screenplay NLP`}
                                  >
                                    <span className="font-bold opacity-75 text-[10px]">{el.category}:</span>
                                    <span>{el.name}</span>
                                    {el.quantity > 1 && (
                                      <span className="px-1 py-0.2 rounded bg-amber-900/50 text-[10px] text-amber-200">
                                        x{el.quantity}
                                      </span>
                                    )}
                                    <span
                                      className="text-[10px] opacity-75 font-mono bg-black/30 px-1 rounded"
                                      title={`AI Detection Confidence: ${confidencePct}%`}
                                    >
                                      {confidencePct}%
                                    </span>
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* 2. Start-to-Finish Shoot Equipment Package */}
                        {displayedEquipment.length > 0 && (
                          <div className="space-y-2 pt-1">
                            <div className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider flex items-center justify-between">
                              <span className="flex items-center gap-1.5">
                                <Camera className="w-3.5 h-3.5 text-cyan-400" />
                                <span>
                                  {isNightScene ? 'Night Shoot Equipment Package' : 'Day Shoot Equipment Package'} ({displayedEquipment.length})
                                </span>
                              </span>
                              <span className="text-[10px] text-slate-400 font-normal">
                                {isNightScene ? '🌙 Low-Light Optics • Key Spotlights • Generator' : '☀️ Daylight Optics • Sun Silks • Ambient Fill'}
                              </span>
                            </div>

                            <div className="flex flex-wrap gap-2 max-h-64 overflow-y-auto pr-1 bg-[#0F1622]/50 p-2.5 rounded-xl border border-[#222E42]">
                              {displayedEquipment.map((el, i) => {
                                const confidencePct = Math.round((el.confidence || 0.95) * 100);
                                const isNightGear = (el.description || '').includes('[NIGHT') || (el.name || '').toLowerCase().includes('night') || (el.name || '').includes('1200') || (el.name || '').toLowerCase().includes('generator') || (el.name || '').toLowerCase().includes('blackout') || (el.name || '').toLowerCase().includes('hazer');
                                const isDayGear = (el.description || '').includes('[DAY') || (el.name || '').toLowerCase().includes('daylight') || (el.name || '').toLowerCase().includes('sun');

                                let badgeStyle = "bg-cyan-500/10 text-cyan-300 border-cyan-500/30 hover:border-cyan-400";
                                let tagLabel = "GEAR";

                                if (isNightGear) {
                                  badgeStyle = "bg-indigo-500/15 text-indigo-200 border-indigo-500/40 hover:border-indigo-400";
                                  tagLabel = "NIGHT RIG";
                                } else if (isDayGear) {
                                  badgeStyle = "bg-amber-500/15 text-amber-200 border-amber-500/40 hover:border-amber-400";
                                  tagLabel = "DAY RIG";
                                }

                                return (
                                  <span
                                    key={i}
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${badgeStyle} transition`}
                                    title={`${el.name}\n${el.description}\nQuantity: ${el.quantity || 1}\nAI Extraction Confidence: ${confidencePct}%`}
                                  >
                                    <span className="font-bold opacity-75 text-[9px] uppercase tracking-wider">{tagLabel}:</span>
                                    <span>{el.name}</span>
                                    {el.quantity > 1 && (
                                      <span className="px-1.5 py-0.2 rounded bg-cyan-900/60 text-[10px] text-cyan-200 font-mono font-bold">
                                        x{el.quantity}
                                      </span>
                                    )}
                                    <span
                                      className="text-[10px] opacity-75 font-mono bg-black/40 px-1 rounded"
                                      title={`AI Extraction Confidence: ${confidencePct}%`}
                                    >
                                      {confidencePct}%
                                    </span>
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                        )}
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
