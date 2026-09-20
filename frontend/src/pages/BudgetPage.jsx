import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  CreditCard,
  DollarSign,
  Plus,
  Save,
  RefreshCw,
  Sliders,
  AlertCircle,
  FileSpreadsheet,
  Check
} from 'lucide-react';
import { budgetService } from '../services/api';

export default function BudgetPage() {
  const { currentProject } = useOutletContext();
  const [budget, setBudget] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editedItems, setEditedItems] = useState({});
  const [showAddModal, setShowAddModal] = useState(false);
  const [newItem, setNewItem] = useState({
    category: 'BELOW_THE_LINE',
    department: 'Camera',
    description: '',
    quantity: 1,
    unit: 'Days',
    unit_rate: 500,
    days_count: 1
  });

  useEffect(() => {
    if (!currentProject?.id) return;
    loadBudget();
  }, [currentProject?.id]);

  const loadBudget = async () => {
    setLoading(true);
    try {
      const data = await budgetService.get(currentProject.id);
      setBudget(data);
    } catch (err) {
      console.error('Failed to load budget:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (id, field, value) => {
    setEditedItems(prev => ({
      ...prev,
      [id]: {
        ...prev[id],
        id,
        [field]: parseFloat(value) || value
      }
    }));
  };

  const handleSaveChanges = async () => {
    if (Object.keys(editedItems).length === 0 || !currentProject?.id) return;
    setSaving(true);
    try {
      const updates = Object.values(editedItems);
      const updatedBudget = await budgetService.updateItems(currentProject.id, updates);
      setBudget(updatedBudget);
      setEditedItems({});
    } catch (err) {
      console.error('Failed to save budget changes:', err);
      alert('Error updating budget.');
    } finally {
      setSaving(false);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newItem.description.trim() || !currentProject?.id) return;
    try {
      const updatedBudget = await budgetService.updateItems(currentProject.id, [newItem]);
      setBudget(updatedBudget);
      setShowAddModal(false);
      setNewItem({
        category: 'BELOW_THE_LINE',
        department: 'Camera',
        description: '',
        quantity: 1,
        unit: 'Days',
        unit_rate: 500,
        days_count: 1
      });
    } catch (err) {
      console.error('Failed to add budget item:', err);
      alert('Error adding budget item.');
    }
  };

  const atlItems = budget?.items?.filter(i => i.category === 'ABOVE_THE_LINE') || [];
  const btlItems = budget?.items?.filter(i => i.category === 'BELOW_THE_LINE') || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              Movie Magic Budgeting-Compatible
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Production Budget Estimation
          </h1>
          <p className="text-xs text-amber-400/90 font-medium">
            {budget?.disclaimer || 'Illustrative planning estimates — user configurable.'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-200 border border-[#27354F] px-4 py-2 rounded-xl text-xs font-semibold transition"
          >
            <Plus className="w-3.5 h-3.5 text-amber-400" />
            <span>Add Line Item</span>
          </button>
          <button
            onClick={handleSaveChanges}
            disabled={Object.keys(editedItems).length === 0 || saving}
            className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md shadow-amber-500/20 transition active:scale-95"
          >
            {saving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            <span>Save Rate Adjustments</span>
          </button>
        </div>
      </div>

      {/* Financial Summary Cards */}
      {budget && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">Subtotal</span>
            <span className="text-2xl font-black text-white font-mono">
              ${budget.subtotal?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">ATL + BTL Direct Costs</span>
          </div>

          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">
              Contingency ({Math.round(budget.contingency_rate * 100)}%)
            </span>
            <span className="text-2xl font-black text-amber-400 font-mono">
              ${budget.contingency_amount?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Unforeseen production variance</span>
          </div>

          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl">
            <span className="text-[11px] text-slate-400 block">
              Taxes & Permits ({Math.round(budget.tax_rate * 100)}%)
            </span>
            <span className="text-2xl font-black text-cyan-400 font-mono">
              ${budget.tax_amount?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Permits, insurance, tax</span>
          </div>

          <div className="bg-[#131B2A] border border-amber-500/30 p-4 rounded-xl shadow-lg bg-gradient-to-tr from-[#131B2A] to-[#1F293D]">
            <span className="text-[11px] text-amber-400 font-bold block uppercase tracking-wider">Grand Total Budget</span>
            <span className="text-2xl font-black text-white font-mono">
              ${budget.grand_total?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[10px] text-emerald-400 font-medium block mt-0.5">Complete Production Estimate</span>
          </div>
        </div>
      )}

      {/* Above-The-Line Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl space-y-2">
        <div className="bg-[#182235] px-6 py-3 border-b border-[#27354F] flex items-center justify-between">
          <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
            Above-The-Line (ATL) — Creative & Principal Talent
          </span>
          <span className="text-xs text-slate-400 font-mono font-bold">
            ${atlItems.reduce((acc, i) => acc + i.subtotal, 0).toLocaleString()}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 uppercase font-semibold text-[10px] border-b border-[#222E42] bg-[#131B2A]">
              <tr>
                <th className="py-2.5 px-4">Code</th>
                <th className="py-2.5 px-4">Department</th>
                <th className="py-2.5 px-4">Description</th>
                <th className="py-2.5 px-4">Qty</th>
                <th className="py-2.5 px-4">Unit</th>
                <th className="py-2.5 px-4">Rate ($)</th>
                <th className="py-2.5 px-4">Days</th>
                <th className="py-2.5 px-4 text-right">Subtotal ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {atlItems.map((item) => (
                <tr key={item.id} className="hover:bg-[#182235]/40 transition">
                  <td className="py-2.5 px-4 font-mono text-slate-400">{item.account_code || '1000'}</td>
                  <td className="py-2.5 px-4 font-semibold text-slate-300">{item.department}</td>
                  <td className="py-2.5 px-4 text-white font-medium">{item.description}</td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="0.5"
                      defaultValue={item.quantity}
                      onChange={(e) => handleFieldChange(item.id, 'quantity', e.target.value)}
                      className="w-16 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">{item.unit}</td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="50"
                      defaultValue={item.unit_rate}
                      onChange={(e) => handleFieldChange(item.id, 'unit_rate', e.target.value)}
                      className="w-24 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="1"
                      defaultValue={item.days_count}
                      onChange={(e) => handleFieldChange(item.id, 'days_count', e.target.value)}
                      className="w-16 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-amber-400">
                    ${item.subtotal?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Below-The-Line Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl space-y-2">
        <div className="bg-[#182235] px-6 py-3 border-b border-[#27354F] flex items-center justify-between">
          <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
            Below-The-Line (BTL) — Crew, Equipment, Locations & Post-Production
          </span>
          <span className="text-xs text-slate-400 font-mono font-bold">
            ${btlItems.reduce((acc, i) => acc + i.subtotal, 0).toLocaleString()}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 uppercase font-semibold text-[10px] border-b border-[#222E42] bg-[#131B2A]">
              <tr>
                <th className="py-2.5 px-4">Code</th>
                <th className="py-2.5 px-4">Department</th>
                <th className="py-2.5 px-4">Description</th>
                <th className="py-2.5 px-4">Qty</th>
                <th className="py-2.5 px-4">Unit</th>
                <th className="py-2.5 px-4">Rate ($)</th>
                <th className="py-2.5 px-4">Days</th>
                <th className="py-2.5 px-4 text-right">Subtotal ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {btlItems.map((item) => (
                <tr key={item.id} className="hover:bg-[#182235]/40 transition">
                  <td className="py-2.5 px-4 font-mono text-slate-400">{item.account_code || '2000'}</td>
                  <td className="py-2.5 px-4 font-semibold text-slate-300">{item.department}</td>
                  <td className="py-2.5 px-4 text-white font-medium">{item.description}</td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="0.5"
                      defaultValue={item.quantity}
                      onChange={(e) => handleFieldChange(item.id, 'quantity', e.target.value)}
                      className="w-16 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">{item.unit}</td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="50"
                      defaultValue={item.unit_rate}
                      onChange={(e) => handleFieldChange(item.id, 'unit_rate', e.target.value)}
                      className="w-24 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4">
                    <input
                      type="number"
                      step="1"
                      defaultValue={item.days_count}
                      onChange={(e) => handleFieldChange(item.id, 'days_count', e.target.value)}
                      className="w-16 bg-[#1A2438] border border-[#27354F] rounded px-2 py-0.5 text-white font-mono text-xs focus:outline-none focus:border-amber-500"
                    />
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono font-bold text-cyan-400">
                    ${item.subtotal?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Line Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Add Budget Line Item</h3>
            <form onSubmit={handleAddItem} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Tier</label>
                <select
                  value={newItem.category}
                  onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                >
                  <option value="ABOVE_THE_LINE">Above-The-Line (ATL)</option>
                  <option value="BELOW_THE_LINE">Below-The-Line (BTL)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Department</label>
                <input
                  type="text"
                  value={newItem.department}
                  onChange={(e) => setNewItem({ ...newItem, department: e.target.value })}
                  placeholder="e.g. Camera, Grip, Transport"
                  required
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Description</label>
                <input
                  type="text"
                  value={newItem.description}
                  onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                  placeholder="e.g. Drone Pilot & Aerial Permitting"
                  required
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Qty</label>
                  <input
                    type="number"
                    value={newItem.quantity}
                    onChange={(e) => setNewItem({ ...newItem, quantity: parseFloat(e.target.value) || 1 })}
                    className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Unit Rate ($)</label>
                  <input
                    type="number"
                    value={newItem.unit_rate}
                    onChange={(e) => setNewItem({ ...newItem, unit_rate: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Days</label>
                  <input
                    type="number"
                    value={newItem.days_count}
                    onChange={(e) => setNewItem({ ...newItem, days_count: parseFloat(e.target.value) || 1 })}
                    className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg p-2 text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#1A2438] text-slate-300 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20"
                >
                  Add to Budget
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
