import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  FileCheck2,
  Calendar,
  Clock,
  MapPin,
  Car,
  CloudSun,
  ShieldAlert,
  Phone,
  Download,
  Users,
  RefreshCw,
  FileText,
  FileSpreadsheet
} from 'lucide-react';
import { documentService } from '../services/api';

export default function CallSheetsPage() {
  const { currentProject } = useOutletContext();
  const [callSheets, setCallSheets] = useState([]);
  const [selectedSheet, setSelectedSheet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadCallSheets();
  }, [currentProject?.id]);

  const loadCallSheets = async () => {
    setLoading(true);
    try {
      const data = await documentService.getCallSheets(currentProject.id);
      setCallSheets(data);
      if (data.length > 0) {
        setSelectedSheet(data[0]);
      }
    } catch (err) {
      console.error('Failed to load call sheets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!currentProject?.id) return;
    setGenerating(true);
    try {
      const data = await documentService.generateCallSheets(currentProject.id);
      setCallSheets(data);
      if (data.length > 0) setSelectedSheet(data[0]);
    } catch (err) {
      console.error('Failed to generate call sheets:', err);
      alert('Error generating call sheets: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              StudioBinder-Inspired Workflow
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Daily Production Call Sheets
          </h1>
          <p className="text-xs text-slate-400">
            Professional daily call sheets with scene lists, talent pickup/set calls, crew schedules, and safety instructions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition"
          >
            {generating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileCheck2 className="w-3.5 h-3.5" />}
            <span>{generating ? 'Compiling Call Sheets...' : 'Regenerate All Call Sheets'}</span>
          </button>
        </div>
      </div>

      {callSheets.length === 0 ? (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center text-xs text-slate-400">
          No call sheets generated yet. Ensure schedule has been solved, then click "Regenerate All Call Sheets".
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Day Selector List */}
          <div className="lg:col-span-3 bg-[#131B2A] border border-[#27354F] rounded-2xl p-4 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Shooting Days ({callSheets.length})
            </div>
            {callSheets.map((cs) => {
              const isSelected = selectedSheet?.id === cs.id;
              return (
                <button
                  key={cs.id}
                  onClick={() => setSelectedSheet(cs)}
                  className={`w-full text-left p-3 rounded-xl text-xs font-semibold transition border ${
                    isSelected
                      ? 'bg-amber-500 text-slate-950 border-amber-500 shadow-md font-bold'
                      : 'bg-[#182235] text-slate-300 border-[#222E42] hover:bg-[#1E2B42]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-extrabold uppercase text-[10px]">DAY {cs.day_number}</span>
                    <span className="font-mono text-[10px]">{cs.general_call_time}</span>
                  </div>
                  <div className="font-bold truncate">{cs.location_name}</div>
                  <div className={`text-[11px] mt-1 ${isSelected ? 'text-slate-900' : 'text-slate-400'}`}>
                    {cs.scenes_summary?.length || 0} Scenes Scheduled
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right: StudioBinder Call Sheet Document View */}
          <div className="lg:col-span-9 bg-[#131B2A] border border-[#27354F] rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
            {selectedSheet && (
              <>
                {/* Top Banner & Export Buttons */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#222E42] pb-4">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-widest text-amber-400 font-bold">
                      {currentProject?.name} • PRODUCTION OFFICE
                    </span>
                    <h2 className="text-xl font-black text-white mt-0.5">
                      OFFICIAL CALL SHEET — DAY {selectedSheet.day_number}
                    </h2>
                    <p className="text-xs text-slate-400 font-mono">{selectedSheet.shoot_date}</p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11px] text-slate-400 font-semibold mr-1 hidden sm:inline">Export Call Sheet:</span>
                    <a
                      href={documentService.getCallSheetPdfUrl(currentProject.id, selectedSheet.id)}
                      download={`CallSheet_Day_${selectedSheet.day_number}.pdf`}
                      title="Download Call Sheet as High-Clarity PDF"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-bold transition shadow-sm hover:scale-[1.02] active:scale-[0.98]"
                    >
                      <FileText className="w-3.5 h-3.5 text-rose-400" />
                      <span>PDF</span>
                    </a>
                    <a
                      href={documentService.getCallSheetDocxUrl(currentProject.id, selectedSheet.id)}
                      download={`CallSheet_Day_${selectedSheet.day_number}.docx`}
                      title="Download Call Sheet as Formatted Microsoft Word (DOCX)"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-bold transition shadow-sm hover:scale-[1.02] active:scale-[0.98]"
                    >
                      <FileCheck2 className="w-3.5 h-3.5 text-blue-400" />
                      <span>DOCX</span>
                    </a>
                    <a
                      href={documentService.getCallSheetXlsxUrl(currentProject.id, selectedSheet.id)}
                      download={`CallSheet_Day_${selectedSheet.day_number}.xlsx`}
                      title="Download Call Sheet as Styled Excel Spreadsheet (XLSX)"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition shadow-sm hover:scale-[1.02] active:scale-[0.98]"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                      <span>EXCEL (.XLSX)</span>
                    </a>
                  </div>
                </div>

                {/* Key Logistics Block */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
                    <span className="text-slate-400 text-[10px] uppercase font-bold flex items-center gap-1 mb-1">
                      <Clock className="w-3.5 h-3.5 text-amber-400" /> General Crew Call
                    </span>
                    <span className="text-base font-black text-white font-mono">{selectedSheet.general_call_time}</span>
                  </div>

                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
                    <span className="text-slate-400 text-[10px] uppercase font-bold flex items-center gap-1 mb-1">
                      <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Shoot Location
                    </span>
                    <span className="text-xs font-bold text-white block truncate">{selectedSheet.location_name}</span>
                    <span className="text-[10px] text-slate-400 truncate block">{selectedSheet.location_address}</span>
                  </div>

                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
                    <span className="text-slate-400 text-[10px] uppercase font-bold flex items-center gap-1 mb-1">
                      <Car className="w-3.5 h-3.5 text-cyan-400" /> Parking & Staging
                    </span>
                    <span className="text-xs text-slate-300 block">{selectedSheet.parking_info}</span>
                  </div>

                  <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
                    <span className="text-slate-400 text-[10px] uppercase font-bold flex items-center gap-1 mb-1">
                      <CloudSun className="w-3.5 h-3.5 text-yellow-400" /> Weather Forecast
                    </span>
                    <span className="text-xs text-slate-300 block">{selectedSheet.weather_placeholder}</span>
                  </div>
                </div>

                {/* Scheduled Scenes Table */}
                <div className="space-y-2">
                  <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Today's Scenes Schedule
                  </div>
                  <div className="border border-[#222E42] rounded-xl overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#182235] text-slate-400 uppercase text-[10px] font-bold">
                        <tr>
                          <th className="py-2.5 px-3">Sc #</th>
                          <th className="py-2.5 px-3">Slugline / Set</th>
                          <th className="py-2.5 px-3">Pages</th>
                          <th className="py-2.5 px-3">Start Time</th>
                          <th className="py-2.5 px-3">Duration</th>
                          <th className="py-2.5 px-3">Complexity</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1E293B]">
                        {selectedSheet.scenes_summary?.map((sc, i) => (
                          <tr key={i} className="hover:bg-[#182235]/40 transition">
                            <td className="py-2.5 px-3 font-bold font-mono text-amber-400">#{sc.scene_number}</td>
                            <td className="py-2.5 px-3 font-medium text-white">{sc.heading}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">{sc.pages}</td>
                            <td className="py-2.5 px-3 font-mono text-cyan-400 font-bold">{sc.start_time}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-400">{sc.duration_mins}m</td>
                            <td className="py-2.5 px-3">
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">
                                {sc.complexity}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Cast Call Times Table */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Cast Call Times & Department Logistics
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {selectedSheet.cast_calls?.length || 0} Actors Scheduled Today
                    </span>
                  </div>
                  <div className="border border-[#222E42] rounded-xl overflow-hidden overflow-x-auto">
                    <table className="w-full text-left text-xs min-w-[760px]">
                      <thead className="bg-[#182235] text-slate-400 uppercase text-[10px] font-bold">
                        <tr>
                          <th className="py-2.5 px-3">Cast #</th>
                          <th className="py-2.5 px-3">Character</th>
                          <th className="py-2.5 px-3">Actor Name</th>
                          <th className="py-2.5 px-3">Scenes Today</th>
                          <th className="py-2.5 px-3">Pickup</th>
                          <th className="py-2.5 px-3">H/MU</th>
                          <th className="py-2.5 px-3">Wardrobe</th>
                          <th className="py-2.5 px-3">On Set</th>
                          <th className="py-2.5 px-3">Status</th>
                          <th className="py-2.5 px-3">Notes</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1E293B]">
                        {selectedSheet.cast_calls?.map((c, i) => (
                          <tr key={i} className="hover:bg-[#182235]/40 transition">
                            <td className="py-2.5 px-3 font-mono text-amber-400 font-bold">#{c.cast_id}</td>
                            <td className="py-2.5 px-3 font-bold text-white">
                              <div className="flex items-center gap-1.5">
                                <span>{c.character_name}</span>
                                {c.role && (
                                  <span className="text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                                    {c.role}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="py-2.5 px-3 text-cyan-200 font-semibold">{c.actor_name}</td>
                            <td className="py-2.5 px-3">
                              <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-300 border border-blue-500/30 text-[10.5px] font-mono font-bold">
                                {c.scenes_today || 'Today\'s Scenes'}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">{c.pickup}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">{c.hair_makeup}</td>
                            <td className="py-2.5 px-3 text-slate-300 text-[11px] truncate max-w-[130px]" title={c.wardrobe}>
                              {c.wardrobe || 'Production Wardrobe'}
                            </td>
                            <td className="py-2.5 px-3 font-mono text-emerald-400 font-black text-sm">{c.on_set}</td>
                            <td className="py-2.5 px-3">
                              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                                {c.status || 'CALLED'}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-slate-400 text-[10.5px] truncate max-w-[140px]" title={c.notes}>
                              {c.notes || 'Sides attached'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Safety & Instructions Block */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="bg-[#182235] p-4 rounded-xl border border-[#222E42] space-y-2">
                    <span className="font-bold text-amber-400 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4" /> Safety & Special Instructions
                    </span>
                    <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {selectedSheet.special_instructions}
                    </p>
                    <div className="text-slate-400 pt-2 border-t border-[#222E42]">
                      <span className="font-bold text-white">Courtesy Lunch: </span>
                      {selectedSheet.meal_break}
                    </div>
                  </div>

                  <div className="bg-[#182235] p-4 rounded-xl border border-[#222E42] space-y-2">
                    <span className="font-bold text-rose-400 flex items-center gap-1.5">
                      <Phone className="w-4 h-4" /> Emergency Logistics & Contacts
                    </span>
                    <div className="space-y-1 text-slate-300">
                      <div>
                        <span className="font-bold text-white">Nearest Hospital: </span>
                        {selectedSheet.nearest_hospital}
                      </div>
                      <div className="pt-1">
                        <span className="font-bold text-white">Key Contacts: </span>
                        {selectedSheet.emergency_contact}
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
