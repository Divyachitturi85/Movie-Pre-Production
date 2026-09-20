import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { Users, Search, Edit2, Mail, Clock, Calendar, Check, X } from 'lucide-react';
import { analysisService } from '../services/api';

export default function CharactersPage() {
  const { currentProject } = useOutletContext();
  const navigate = useNavigate();

  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editingChar, setEditingChar] = useState(null);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadCharacters();
  }, [currentProject?.id]);

  const loadCharacters = async () => {
    setLoading(true);
    try {
      const data = await analysisService.getCharacters(currentProject.id);
      setCharacters(data);
    } catch (err) {
      console.error('Failed to load characters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingChar || !currentProject?.id) return;
    try {
      await analysisService.updateCharacter(currentProject.id, editingChar.id, {
        role: editingChar.role,
        costume_requirements: editingChar.costume_requirements,
        makeup_requirements: editingChar.makeup_requirements,
        notes: editingChar.notes
      });
      await loadCharacters();
      setEditingChar(null);
    } catch (err) {
      console.error('Failed to update character:', err);
      alert('Error updating character.');
    }
  };

  const filtered = characters.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Users className="w-6 h-6 text-cyan-400" />
            <span>Cast & Character Breakdown</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Speaking roles, dialogue presence, screen time estimates, and required talent shooting days.
          </p>
        </div>

        <button
          onClick={() => navigate('/callbacks')}
          className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 px-4 py-2 rounded-xl text-xs font-bold transition shadow-md shadow-amber-500/20"
        >
          <Mail className="w-3.5 h-3.5" />
          <span>Generate Callback Letters</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex items-center gap-3">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search character name or role..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none flex-1"
        />
      </div>

      {/* Characters Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#182235] text-slate-400 uppercase tracking-wider font-bold border-b border-[#27354F] text-[11px]">
              <tr>
                <th className="py-3 px-4">Character Name</th>
                <th className="py-3 px-4">Role Tier</th>
                <th className="py-3 px-4">Scene Count</th>
                <th className="py-3 px-4">Dialogue Count</th>
                <th className="py-3 px-4">Est. Screen Time</th>
                <th className="py-3 px-4">Required Shoot Days</th>
                <th className="py-3 px-4">Wardrobe / Makeup</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222E42]">
              {filtered.map((char) => (
                <tr key={char.id} className="hover:bg-[#182235]/60 transition">
                  <td className="py-3.5 px-4 font-bold text-white flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center font-black text-xs">
                      {char.name.charAt(0)}
                    </div>
                    <span>{char.name}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                      char.role === 'LEAD'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : char.role === 'SUPPORTING'
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {char.role}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-mono font-semibold">
                    {char.scene_count} scenes
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-mono">
                    {char.dialogue_count}
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 font-mono">
                    {char.estimated_screen_time_minutes} mins
                  </td>
                  <td className="py-3.5 px-4 text-amber-400 font-mono font-bold">
                    {char.required_shooting_days} days
                  </td>
                  <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate" title={char.costume_requirements}>
                    {char.costume_requirements || 'Standard'}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setEditingChar({ ...char })}
                      className="p-1.5 rounded-lg bg-[#1A2438] hover:bg-[#27354F] text-slate-300 hover:text-white transition"
                      title="Edit Character Requirements"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Modal */}
      {editingChar && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Edit Character: {editingChar.name}</h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Role Classification</label>
                <select
                  value={editingChar.role}
                  onChange={(e) => setEditingChar({ ...editingChar, role: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="LEAD">LEAD</option>
                  <option value="SUPPORTING">SUPPORTING</option>
                  <option value="MINOR">MINOR</option>
                  <option value="EXTRA">EXTRA</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Costume Requirements</label>
                <textarea
                  value={editingChar.costume_requirements || ''}
                  onChange={(e) => setEditingChar({ ...editingChar, costume_requirements: e.target.value })}
                  rows={2}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Makeup & Prosthetics</label>
                <textarea
                  value={editingChar.makeup_requirements || ''}
                  onChange={(e) => setEditingChar({ ...editingChar, makeup_requirements: e.target.value })}
                  rows={2}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setEditingChar(null)}
                className="px-4 py-2 rounded-xl bg-[#1A2438] text-slate-300 font-semibold text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
