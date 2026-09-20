import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { BookOpen, Layers, Search, Clock, MapPin, Hash, Sparkles } from 'lucide-react';
import { analysisService, scriptService } from '../services/api';

export default function ScriptViewerPage() {
  const { currentProject } = useOutletContext();
  const navigate = useNavigate();

  const [scenes, setScenes] = useState([]);
  const [script, setScript] = useState(null);
  const [selectedScene, setSelectedScene] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadScriptData();
  }, [currentProject?.id]);

  const loadScriptData = async () => {
    setLoading(true);
    try {
      const [scData, scScript] = await Promise.all([
        analysisService.getScenes(currentProject.id).catch(() => []),
        scriptService.get(currentProject.id).catch(() => null)
      ]);
      setScenes(scData);
      setScript(scScript);
      if (scData.length > 0) {
        setSelectedScene(scData[0]);
      }
    } catch (err) {
      console.error('Failed to load scenes:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredScenes = scenes.filter(s =>
    (s.heading || '').toLowerCase().includes(search.toLowerCase()) ||
    (s.location_name || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <BookOpen className="w-6 h-6 text-amber-400" />
            <span>Screenplay Reader & Slugline Inspector</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Standard Celtx-compatible screenplay view with slugline tokenization and scene segmentation.
          </p>
        </div>

        <button
          onClick={() => navigate('/breakdown')}
          className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition self-start sm:self-auto"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Switch to StudioBinder Breakdown</span>
        </button>
      </div>

      {scenes.length === 0 ? (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center">
          <BookOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-white mb-1">No Screenplay Parsed</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Upload a script PDF or load the demo project to inspect formatted scenes.
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="px-4 py-2 bg-amber-500 text-slate-950 text-xs font-bold rounded-xl"
          >
            Upload Script
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Scene Index List */}
          <div className="lg:col-span-4 bg-[#131B2A] border border-[#27354F] rounded-2xl p-4 space-y-3 max-h-[750px] flex flex-col">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search scene # or location..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-[#1A2438] border border-[#27354F] rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="text-[11px] font-semibold text-slate-400 flex justify-between px-1">
              <span>{filteredScenes.length} SCENES</span>
              <span>EST. {scenes.reduce((acc, s) => acc + (s.estimated_pages || 0), 0).toFixed(1)} PGS</span>
            </div>

            <div className="space-y-1.5 overflow-y-auto flex-1 pr-1">
              {filteredScenes.map((sc) => {
                const isSelected = selectedScene?.id === sc.id;
                return (
                  <button
                    key={sc.id}
                    onClick={() => setSelectedScene(sc)}
                    className={`w-full text-left p-2.5 rounded-xl text-xs transition border ${
                      isSelected
                        ? 'bg-amber-500 text-slate-950 border-amber-500 shadow-md font-bold'
                        : 'bg-[#182235] text-slate-300 border-[#222E42] hover:bg-[#1E2B42] hover:text-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded ${
                        isSelected ? 'bg-black/20 text-slate-950' : 'bg-slate-800 text-amber-400'
                      }`}>
                        SCENE {sc.scene_number}
                      </span>
                      <span className="text-[10px] opacity-75 font-mono">
                        {sc.estimated_duration_minutes}m • {sc.estimated_pages} pgs
                      </span>
                    </div>
                    <div className="font-semibold truncate">{sc.heading}</div>
                    <div className={`text-[11px] mt-1 flex items-center gap-2 ${isSelected ? 'text-slate-900' : 'text-slate-400'}`}>
                      <span>{sc.interior_exterior}</span>
                      <span>•</span>
                      <span>{sc.time_of_day}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Authentic Screenplay Viewer Page */}
          <div className="lg:col-span-8 bg-[#131B2A] border border-[#27354F] rounded-2xl p-6 sm:p-8 shadow-xl min-h-[600px]">
            {selectedScene ? (
              <div className="space-y-6">
                {/* Scene Meta Bar */}
                <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#182235] border border-[#27354F]">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-lg bg-amber-500 text-slate-950 font-black text-xs">
                      SCENE {selectedScene.scene_number}
                    </span>
                    <span className="text-xs font-bold text-slate-200">
                      {selectedScene.interior_exterior} / {selectedScene.time_of_day}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1 font-mono">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      {selectedScene.estimated_duration_minutes} mins
                    </span>
                    <span className="flex items-center gap-1 font-mono">
                      <Hash className="w-3.5 h-3.5 text-cyan-400" />
                      {selectedScene.estimated_pages} pages
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      selectedScene.complexity_level === 'HIGH' || selectedScene.complexity_level === 'VERY HIGH'
                        ? 'bg-rose-500/20 text-rose-400'
                        : 'bg-emerald-500/20 text-emerald-400'
                    }`}>
                      {selectedScene.complexity_level} Complexity
                    </span>
                  </div>
                </div>

                {/* Formatted Script Page Body (Courier Prime) */}
                <div className="bg-[#0F1420] border border-[#1E293B] rounded-xl p-8 sm:p-10 font-screenplay text-[13px] text-slate-200 leading-relaxed shadow-inner overflow-x-auto">
                  <div className="text-amber-400 font-bold tracking-wide mb-4 uppercase">
                    {selectedScene.heading}
                  </div>

                  <div className="whitespace-pre-wrap space-y-3 font-normal">
                    {selectedScene.raw_content ? (
                      selectedScene.raw_content
                    ) : (
                      <div>{selectedScene.action_text}</div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-slate-500 text-xs">Select a scene from the list to view</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
