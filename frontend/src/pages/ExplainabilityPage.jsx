import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Cpu,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info,
  Sparkles,
  Zap,
  Layers,
  Calendar
} from 'lucide-react';
import { documentService } from '../services/api';

const STAGES = [
  'ALL',
  'OCR',
  'PDF_EXTRACTION',
  'NER_CHARACTER',
  'NER_LOCATION',
  'NER_PROP',
  'NER_COSTUME',
  'NER_VEHICLE',
  'NER_VFX',
  'RESOURCE_EQUIPMENT',
  'COMPLEXITY_SCORING',
  'ORTOOLS_SCHEDULING',
  'BUDGET_ESTIMATION'
];

export default function ExplainabilityPage() {
  const { currentProject } = useOutletContext();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeStage, setActiveStage] = useState('ALL');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!currentProject?.id) return;
    loadExplainability();
  }, [currentProject?.id]);

  const loadExplainability = async () => {
    setLoading(true);
    try {
      const data = await documentService.getExplainability(currentProject.id);
      setRecords(data);
    } catch (err) {
      console.error('Failed to load explainability:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = records.filter(r => {
    const matchesStage = activeStage === 'ALL' || r.stage === activeStage;
    const matchesSearch =
      (r.target_entity || '').toLowerCase().includes(search.toLowerCase()) ||
      (r.ai_method || '').toLowerCase().includes(search.toLowerCase()) ||
      (r.output_detected || '').toLowerCase().includes(search.toLowerCase());
    return matchesStage && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-[#27354F] pb-4">
        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase font-bold tracking-widest bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-2 py-0.5 rounded-full">
            Academic Demonstration Audit Trail
          </span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2.5">
          <Cpu className="w-6 h-6 text-cyan-400" />
          <span>AI Decision Explainability & Audit Log</span>
        </h1>
        <p className="text-xs text-slate-400">
          Transparent logging of every AI model, linguistic parser, and OR-Tools optimization constraint used across the pipeline.
        </p>
      </div>

      {/* Stage Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {STAGES.map(stage => (
          <button
            key={stage}
            onClick={() => setActiveStage(stage)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition whitespace-nowrap ${
              activeStage === stage
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                : 'bg-[#131B2A] text-slate-300 hover:bg-[#1A2438] border border-[#27354F]'
            }`}
          >
            {stage.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Search Bar */}
      <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex items-center gap-3">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Filter by target entity, AI method, or output..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none flex-1"
        />
      </div>

      {/* Explainability Records Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#182235] text-slate-400 uppercase tracking-wider font-bold border-b border-[#27354F] text-[10px]">
              <tr>
                <th className="py-3 px-4">Stage</th>
                <th className="py-3 px-4">Target Entity</th>
                <th className="py-3 px-4">AI Method / Model</th>
                <th className="py-3 px-4">Detected Output</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Fallback Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222E42]">
              {filtered.map((r) => (
                <tr key={r.id} className="hover:bg-[#182235]/60 transition">
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-800 text-amber-400 font-mono">
                      {r.stage}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-bold text-white max-w-xs truncate">{r.target_entity}</td>
                  <td className="py-3 px-4 text-cyan-400 font-mono text-[11px] max-w-xs">{r.ai_method}</td>
                  <td className="py-3 px-4 text-slate-300 max-w-sm truncate" title={r.output_detected}>
                    {r.output_detected}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                    {Math.round((r.confidence || 0.9) * 100)}%
                  </td>
                  <td className="py-3 px-4">
                    {r.fallback_used ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                        <AlertTriangle className="w-3 h-3" />
                        <span>Rule Fallback</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Primary Model</span>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
