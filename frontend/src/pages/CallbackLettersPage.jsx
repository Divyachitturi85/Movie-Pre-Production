import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Mail,
  Users,
  Download,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  RefreshCw,
  FileText,
  Check,
  Send
} from 'lucide-react';
import { documentService, analysisService } from '../services/api';

export default function CallbackLettersPage() {
  const { currentProject } = useOutletContext();
  const [letters, setLetters] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [selectedLetter, setSelectedLetter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // New Single Callback Form State
  const [newCallback, setNewCallback] = useState({
    character_name: '',
    actor_name: '',
    role_type: 'LEAD',
    callback_date: 'Monday, October 12, 2026',
    callback_time: '10:30 AM EST',
    location: 'Aurora Casting Studios, Studio 4B / Zoom',
    sides_reference: 'Scenes 2 & 5 (Attached)',
    what_to_prepare: 'Memorize attached sides. Prepare for cold-read adjustments with Director.',
    contact_person: 'Sarah Jenkins (Casting Director)',
    contact_email: 'casting@auroraproductions.com',
    contact_phone: '+1 (555) 012-3456'
  });

  useEffect(() => {
    if (!currentProject?.id) return;
    loadCallbackData();
  }, [currentProject?.id]);

  const loadCallbackData = async () => {
    setLoading(true);
    try {
      const [lData, cData] = await Promise.all([
        documentService.getCallbacks(currentProject.id).catch(() => []),
        analysisService.getCharacters(currentProject.id).catch(() => [])
      ]);
      setLetters(lData);
      setCharacters(cData);
      if (lData.length > 0) setSelectedLetter(lData[0]);
      if (cData.length > 0 && !newCallback.character_name) {
        setNewCallback(prev => ({
          ...prev,
          character_name: cData[0].name,
          role_type: cData[0].role
        }));
      }
    } catch (err) {
      console.error('Failed to load callbacks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBulk = async () => {
    if (!currentProject?.id) return;
    setGenerating(true);
    try {
      const data = await documentService.generateCallbacks(currentProject.id);
      setLetters(data);
      if (data.length > 0) setSelectedLetter(data[0]);
    } catch (err) {
      console.error('Bulk generation failed:', err);
      alert('Error generating callback letters: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateSingle = async (e) => {
    e.preventDefault();
    if (!newCallback.actor_name.trim() || !newCallback.character_name || !currentProject?.id) return;
    setGenerating(true);
    try {
      const created = await documentService.createCallback(currentProject.id, newCallback);
      setLetters(prev => [created, ...prev]);
      setSelectedLetter(created);
      alert('Callback letter generated successfully!');
    } catch (err) {
      console.error('Single creation failed:', err);
      alert('Error creating callback letter: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              Talent Audition Output
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Audition Callback Letter Studio
          </h1>
          <p className="text-xs text-slate-400">
            Generate formal callback invitations for auditioning talent with allocated appointment times and sides.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateBulk}
            disabled={generating}
            className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-200 border border-[#27354F] px-4 py-2 rounded-xl text-xs font-semibold transition"
          >
            {generating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-amber-400" />}
            <span>Auto-Generate All ({characters.length} Cast)</span>
          </button>
          <a
            href={documentService.getCallbacksPdfUrl(currentProject.id)}
            download="10_Callback_Letters.pdf"
            className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download All Letters (PDF)</span>
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Form & Existing Letters Selector */}
        <div className="lg:col-span-4 space-y-6">
          {/* Custom Callback Creator Form */}
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Mail className="w-4 h-4 text-amber-400" />
              <span>Compose Custom Callback</span>
            </h3>

            <form onSubmit={handleCreateSingle} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Select Character</label>
                <select
                  value={newCallback.character_name}
                  onChange={(e) => {
                    const c = characters.find(x => x.name === e.target.value);
                    setNewCallback({
                      ...newCallback,
                      character_name: e.target.value,
                      role_type: c?.role || 'LEAD'
                    });
                  }}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                >
                  {characters.map(c => (
                    <option key={c.id} value={c.name}>
                      {c.name} ({c.role})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Actor / Candidate Name</label>
                <input
                  type="text"
                  placeholder="e.g. Alex Rivera"
                  value={newCallback.actor_name}
                  onChange={(e) => setNewCallback({ ...newCallback, actor_name: e.target.value })}
                  required
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Date</label>
                  <input
                    type="text"
                    value={newCallback.callback_date}
                    onChange={(e) => setNewCallback({ ...newCallback, callback_date: e.target.value })}
                    className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Time Slot</label>
                  <input
                    type="text"
                    value={newCallback.callback_time}
                    onChange={(e) => setNewCallback({ ...newCallback, callback_time: e.target.value })}
                    className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Audition Location / Link</label>
                <input
                  type="text"
                  value={newCallback.location}
                  onChange={(e) => setNewCallback({ ...newCallback, location: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Sides Reference</label>
                <input
                  type="text"
                  value={newCallback.sides_reference}
                  onChange={(e) => setNewCallback({ ...newCallback, sides_reference: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                />
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20 transition active:scale-95 flex items-center justify-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Generate Callback Letter</span>
              </button>
            </form>
          </div>

          {/* Letter List */}
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-4 space-y-2 max-h-80 overflow-y-auto">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Generated Letters ({letters.length})
            </div>
            {letters.map((l) => {
              const isSelected = selectedLetter?.id === l.id;
              return (
                <button
                  key={l.id}
                  onClick={() => setSelectedLetter(l)}
                  className={`w-full text-left p-2.5 rounded-xl text-xs transition border ${
                    isSelected
                      ? 'bg-amber-500 text-slate-950 border-amber-500 shadow-md font-bold'
                      : 'bg-[#182235] text-slate-300 border-[#222E42] hover:bg-[#1E2B42]'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold">{l.actor_name}</span>
                    <span className="font-mono text-[10px]">{l.callback_time}</span>
                  </div>
                  <div className={`text-[11px] ${isSelected ? 'text-slate-900' : 'text-slate-400'}`}>
                    Role: <span className="font-semibold">{l.character_name}</span> ({l.role_type})
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: Formal Callback Letter Document Preview */}
        <div className="lg:col-span-8 bg-[#131B2A] border border-[#27354F] rounded-2xl p-6 sm:p-10 shadow-2xl min-h-[600px] flex flex-col justify-between">
          {selectedLetter ? (
            <div className="space-y-6">
              {/* Top Producer Heading */}
              <div className="border-b border-[#222E42] pb-6 flex items-start justify-between">
                <div>
                  <div className="text-[10px] uppercase font-mono tracking-widest text-amber-400 font-bold">
                    OFFICIAL AUDITION NOTICE • TALENT AFFAIRS
                  </div>
                  <h2 className="text-xl font-black text-white mt-1">
                    AUDITION CALLBACK INVITATION
                  </h2>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Production: <span className="text-slate-200 font-semibold">{currentProject?.name}</span>
                  </div>
                </div>

                <div className="text-right text-xs">
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                    {selectedLetter.status}
                  </span>
                  <div className="text-slate-400 text-[11px] mt-1 font-mono">{selectedLetter.callback_date}</div>
                </div>
              </div>

              {/* Formatted Letter Body (Paper Aesthetic) */}
              <div className="bg-[#0F1420] border border-[#1E293B] rounded-xl p-8 text-xs text-slate-200 font-serif leading-relaxed space-y-4 shadow-inner">
                <div className="whitespace-pre-wrap leading-6 text-slate-300">
                  {selectedLetter.letter_body}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-xs text-slate-500">
              No callback letter selected. Select one from the list or compose a new one.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
