import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import {
  Calendar,
  Clock,
  MapPin,
  AlertCircle,
  RefreshCw,
  Sliders,
  CheckCircle2,
  FileCheck2,
  Cpu,
  Layers,
  Sparkles
} from 'lucide-react';
import { scheduleService } from '../services/api';

export default function SchedulePage() {
  const { currentProject } = useOutletContext();
  const navigate = useNavigate();

  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [maxHours, setMaxHours] = useState(10.0);
  const [prioritizeLoc, setPrioritizeLoc] = useState(true);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadSchedule();
  }, [currentProject?.id]);

  const loadSchedule = async () => {
    setLoading(true);
    try {
      const data = await scheduleService.get(currentProject.id);
      setSchedule(data);
    } catch (err) {
      console.error('Schedule not found:', err);
      setSchedule(null);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!currentProject?.id) return;
    setOptimizing(true);
    try {
      const updated = await scheduleService.optimize(currentProject.id, {
        max_daily_hours: parseFloat(maxHours),
        prioritize_locations: prioritizeLoc
      });
      setSchedule(updated);
    } catch (err) {
      console.error('Optimization failed:', err);
      alert('Error running OR-Tools optimization: ' + (err.response?.data?.detail || err.message));
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full">
              Google OR-Tools CP-SAT
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Shooting Schedule Optimization
          </h1>
          <p className="text-xs text-slate-400">
            Constraint programming solver minimizing shooting days, location moves, and cast idle time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/stripboard')}
            className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-200 border border-[#27354F] px-4 py-2 rounded-xl text-xs font-semibold transition"
          >
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            <span>Movie Magic Stripboard</span>
          </button>
          <button
            onClick={() => navigate('/call-sheets')}
            className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition"
          >
            <FileCheck2 className="w-3.5 h-3.5" />
            <span>Generate Call Sheets</span>
          </button>
        </div>
      </div>

      {/* Solver Controls Panel */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-5 shadow-md flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-6 text-xs">
          <div className="flex items-center gap-3">
            <Sliders className="w-4 h-4 text-amber-400" />
            <span className="font-semibold text-slate-300">Max Daily Shoot Hours:</span>
            <input
              type="range"
              min="6.0"
              max="14.0"
              step="0.5"
              value={maxHours}
              onChange={(e) => setMaxHours(e.target.value)}
              className="w-28 accent-amber-500"
            />
            <span className="font-mono text-amber-400 font-bold">{maxHours}h</span>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={prioritizeLoc}
              onChange={(e) => setPrioritizeLoc(e.target.checked)}
              className="rounded bg-[#1A2438] border-[#27354F] text-amber-500 focus:ring-0"
            />
            <span className="text-slate-300">Prioritize Location Continuity (Fewer Moves)</span>
          </label>
        </div>

        <button
          onClick={handleOptimize}
          disabled={optimizing}
          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold px-5 py-2 rounded-xl text-xs shadow-md shadow-emerald-600/20 transition"
        >
          {optimizing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          <span>{optimizing ? 'Solving with CP-SAT...' : 'Re-Run Optimization'}</span>
        </button>
      </div>

      {/* Schedule Summary Bar */}
      {schedule && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">Total Shooting Days</span>
            <span className="text-2xl font-black text-white">{schedule.total_days}</span>
            <span className="text-[10px] text-emerald-400 block mt-0.5">Optimal Solution</span>
          </div>

          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">Total Shooting Hours</span>
            <span className="text-2xl font-black text-white">{schedule.total_shooting_hours}h</span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Incl. setup & breaks</span>
          </div>

          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">Company Moves</span>
            <span className="text-2xl font-black text-white">{schedule.total_company_moves}</span>
            <span className="text-[10px] text-amber-400 block mt-0.5">Inter-day transitions</span>
          </div>

          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">CP-SAT Solve Time</span>
            <span className="text-2xl font-black text-cyan-400 font-mono">{schedule.solver_time_seconds}s</span>
            <span className="text-[10px] text-cyan-400 block mt-0.5">{schedule.optimization_status}</span>
          </div>
        </div>
      )}

      {/* Mathematical Explanation Card */}
      {schedule?.notes && (
        <div className="bg-[#182235]/60 border border-[#27354F] rounded-xl p-4 text-xs text-slate-300 space-y-1">
          <div className="font-bold text-amber-400 flex items-center gap-2">
            <Cpu className="w-4 h-4" />
            <span>OR-Tools Optimization Explanation</span>
          </div>
          <p className="text-slate-400">{schedule.notes}</p>
        </div>
      )}

      {/* Day by Day Cards */}
      {schedule?.shooting_days?.length > 0 ? (
        <div className="space-y-6">
          {schedule.shooting_days.map((day) => (
            <div
              key={day.id}
              className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-lg"
            >
              {/* Day Header */}
              <div className="bg-[#182235] p-4 sm:px-6 border-b border-[#27354F] flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500 text-slate-950 font-black text-base flex items-center justify-center">
                    D{day.day_number}
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-white">{day.shoot_date || `Shoot Day ${day.day_number}`}</h3>
                    <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                      <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{day.primary_location || 'Main Stage'}</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs">
                  <div className="bg-[#1A2438] px-3 py-1.5 rounded-lg border border-[#27354F]">
                    <span className="text-slate-400 text-[10px] block">Call Time</span>
                    <span className="font-bold text-white">{day.call_time}</span>
                  </div>
                  <div className="bg-[#1A2438] px-3 py-1.5 rounded-lg border border-[#27354F]">
                    <span className="text-slate-400 text-[10px] block">Est. Wrap</span>
                    <span className="font-bold text-white">{day.wrap_time}</span>
                  </div>
                  <div className="bg-[#1A2438] px-3 py-1.5 rounded-lg border border-[#27354F]">
                    <span className="text-slate-400 text-[10px] block">Meal Break</span>
                    <span className="font-bold text-amber-400">{day.meal_break_time}</span>
                  </div>
                  <div className="bg-[#1A2438] px-3 py-1.5 rounded-lg border border-[#27354F]">
                    <span className="text-slate-400 text-[10px] block">Company Moves</span>
                    <span className={`font-bold ${day.company_moves_count > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {day.company_moves_count}
                    </span>
                  </div>
                </div>
              </div>

              {/* Day Scenes Table */}
              <div className="p-4 sm:p-6 space-y-3">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Scheduled Shooting Sequence ({day.scheduled_scenes?.length || 0} Scenes)
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#182235]/80 text-slate-400 uppercase font-semibold text-[10px] border-b border-[#222E42]">
                      <tr>
                        <th className="py-2.5 px-3">Order</th>
                        <th className="py-2.5 px-3">Scene #</th>
                        <th className="py-2.5 px-3">Slugline / Heading</th>
                        <th className="py-2.5 px-3">Location</th>
                        <th className="py-2.5 px-3">Est. Start Time</th>
                        <th className="py-2.5 px-3">Duration</th>
                        <th className="py-2.5 px-3">Complexity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1E293B]">
                      {day.scheduled_scenes?.map((ss) => (
                        <tr key={ss.id} className="hover:bg-[#182235]/40 transition">
                          <td className="py-2.5 px-3 font-bold text-slate-400 font-mono">#{ss.sequence_order}</td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-bold font-mono">
                              Sc {ss.scene_number || ss.scene_id}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-white">
                            {ss.heading || `Scene ${ss.scene_number}`}
                          </td>
                          <td className="py-2.5 px-3 text-slate-300">
                            {ss.location_name}
                            {ss.company_move_before && (
                              <span className="ml-2 text-[10px] text-amber-400 font-bold bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
                                Move Prior
                              </span>
                            )}
                          </td>
                          <td className="py-2.5 px-3 font-mono text-cyan-400 font-bold">{ss.estimated_start_time}</td>
                          <td className="py-2.5 px-3 font-mono text-slate-300">{ss.estimated_duration_minutes} mins</td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">
                              {ss.complexity_level || 'LOW'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-12 text-center text-xs text-slate-400">
          No schedule generated yet. Click "Re-Run Optimization" to solve with Google OR-Tools.
        </div>
      )}
    </div>
  );
}
