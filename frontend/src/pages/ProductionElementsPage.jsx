import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Package,
  Search,
  Filter,
  Plus,
  Trash2,
  Cpu,
  Sparkles,
  Zap,
  Car,
  Camera,
  Layers
} from 'lucide-react';
import { analysisService } from '../services/api';

const CATEGORIES = ['ALL', 'PROP', 'COSTUME', 'VEHICLE', 'EQUIPMENT', 'VFX', 'SFX', 'WEAPON', 'ANIMAL'];

export default function ProductionElementsPage() {
  const { currentProject } = useOutletContext();
  const [elements, setElements] = useState([]);
  const [scenes, setScenes] = useState([]);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEl, setNewEl] = useState({ category: 'PROP', name: '', description: '', scene_id: '', quantity: 1 });

  useEffect(() => {
    if (!currentProject?.id) return;
    loadElements();
  }, [currentProject?.id]);

  const loadElements = async () => {
    setLoading(true);
    try {
      const [elData, scData] = await Promise.all([
        analysisService.getElements(currentProject.id),
        analysisService.getScenes(currentProject.id)
      ]);
      setElements(elData);
      setScenes(scData);
    } catch (err) {
      console.error('Failed to load elements:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateElement = async (e) => {
    e.preventDefault();
    if (!newEl.name.trim() || !currentProject?.id) return;
    try {
      await analysisService.createElement(currentProject.id, {
        category: newEl.category,
        name: newEl.name,
        description: newEl.description,
        scene_id: newEl.scene_id ? parseInt(newEl.scene_id) : null,
        quantity: parseInt(newEl.quantity) || 1
      });
      await loadElements();
      setShowAddModal(false);
      setNewEl({ category: 'PROP', name: '', description: '', scene_id: '', quantity: 1 });
    } catch (err) {
      console.error('Failed to create element:', err);
      alert('Error creating element.');
    }
  };

  const handleDeleteElement = async (id) => {
    if (!confirm('Are you sure you want to remove this item?')) return;
    try {
      await analysisService.deleteElement(currentProject.id, id);
      setElements(elements.filter(e => e.id !== id));
    } catch (err) {
      console.error('Failed to delete element:', err);
    }
  };

  const filtered = elements.filter(el => {
    const matchesCat = activeCategory === 'ALL' || el.category === activeCategory;
    const matchesSearch =
      el.name.toLowerCase().includes(search.toLowerCase()) ||
      (el.description || '').toLowerCase().includes(search.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Package className="w-6 h-6 text-amber-400" />
            <span>Production Elements & Asset Tracker</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Props, costumes, vehicles, camera/lighting equipment, and VFX/SFX requirements extracted from screenplay.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Custom Asset</span>
        </button>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition whitespace-nowrap ${
              activeCategory === cat
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                : 'bg-[#131B2A] text-slate-300 hover:bg-[#1A2438] border border-[#27354F]'
            }`}
          >
            {cat} {cat !== 'ALL' && `(${elements.filter(e => e.category === cat).length})`}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex items-center gap-3">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search by asset name or description..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none flex-1"
        />
      </div>

      {/* Elements Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#182235] text-slate-400 uppercase tracking-wider font-bold border-b border-[#27354F] text-[11px]">
              <tr>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Element Name</th>
                <th className="py-3 px-4">Quantity</th>
                <th className="py-3 px-4">Scene Ref</th>
                <th className="py-3 px-4">AI Confidence</th>
                <th className="py-3 px-4">Extraction Method</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222E42]">
              {filtered.map((el) => {
                const sc = scenes.find(s => s.id === el.scene_id);
                return (
                  <tr key={el.id} className="hover:bg-[#182235]/60 transition">
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-800 text-amber-400 font-mono">
                        {el.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-white">
                      <div>{el.name}</div>
                      {el.description && (
                        <div className="text-[11px] text-slate-400 font-normal mt-0.5">{el.description}</div>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300 font-semibold">{el.quantity}</td>
                    <td className="py-3 px-4 font-mono text-cyan-400">
                      {sc ? `Scene ${sc.scene_number}` : 'Production Asset'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-emerald-400 font-mono font-bold">
                        {Math.round((el.confidence || 0.85) * 100)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">
                      {el.extraction_source || 'NLP_SERVICE'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDeleteElement(el.id)}
                        className="p-1.5 rounded-lg bg-[#1A2438] hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Add Custom Production Element</h3>
            <form onSubmit={handleCreateElement} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Category</label>
                <select
                  value={newEl.category}
                  onChange={(e) => setNewEl({ ...newEl, category: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="PROP">PROP</option>
                  <option value="COSTUME">COSTUME</option>
                  <option value="VEHICLE">VEHICLE</option>
                  <option value="EQUIPMENT">EQUIPMENT</option>
                  <option value="VFX">VFX</option>
                  <option value="SFX">SFX</option>
                  <option value="WEAPON">WEAPON</option>
                  <option value="ANIMAL">ANIMAL</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Item Name</label>
                <input
                  type="text"
                  placeholder="e.g. Quantum Holo-Pad"
                  value={newEl.name}
                  onChange={(e) => setNewEl({ ...newEl, name: e.target.value })}
                  required
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Assigned Scene</label>
                <select
                  value={newEl.scene_id}
                  onChange={(e) => setNewEl({ ...newEl, scene_id: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="">General Production Asset (All Scenes)</option>
                  {scenes.map(s => (
                    <option key={s.id} value={s.id}>
                      Scene {s.scene_number}: {s.heading}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Description / Notes</label>
                <textarea
                  value={newEl.description}
                  onChange={(e) => setNewEl({ ...newEl, description: e.target.value })}
                  rows={2}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#1A2438] text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20"
                >
                  Add Element
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
