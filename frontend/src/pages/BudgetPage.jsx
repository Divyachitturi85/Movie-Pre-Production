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
  Check,
  Eye,
  EyeOff,
  TrendingUp,
  Sparkles,
  ArrowDownRight,
  Tag
} from 'lucide-react';
import { budgetService } from '../services/api';

export default function BudgetPage() {
  const { currentProject } = useOutletContext();
  const [budget, setBudget] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editedItems, setEditedItems] = useState({});
  const [showAddModal, setShowAddModal] = useState(false);
  const [showActualCost, setShowActualCost] = useState(false);
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

  // Helper to compute both optimised and actual rates for an item (including live user edits)
  const getItemMetrics = (item) => {
    const isATL = item.category === 'ABOVE_THE_LINE';
    const edited = editedItems[item.id] || {};
    const qty = edited.quantity !== undefined ? edited.quantity : (item.quantity ?? 1);
    const days = edited.days_count !== undefined ? edited.days_count : (item.days_count ?? 1);
    const optRate = edited.unit_rate !== undefined ? edited.unit_rate : (item.unit_rate ?? 0);

    // Unoptimised standard retail day-rate without pre-production schedule consolidation
    // Industry baseline: ~15% higher for ATL, ~22% higher for BTL
    const markup = isATL ? 1.15 : 1.22;
    const actualRate = item.actual_unit_rate || Math.round(optRate * markup);

    const optSubtotal = Math.round(qty * optRate * days * 100) / 100;
    const actualSubtotal = Math.round(qty * actualRate * days * 100) / 100;
    const savings = Math.max(0, actualSubtotal - optSubtotal);

    return {
      qty,
      days,
      optRate,
      actualRate,
      optSubtotal,
      actualSubtotal,
      savings
    };
  };

  const atlItems = budget?.items?.filter(i => i.category === 'ABOVE_THE_LINE') || [];
  const btlItems = budget?.items?.filter(i => i.category === 'BELOW_THE_LINE') || [];

  // Compute live aggregates across all items
  const allItems = budget?.items || [];
  let totalOptSubtotal = 0;
  let totalActualSubtotal = 0;
  allItems.forEach(item => {
    const m = getItemMetrics(item);
    totalOptSubtotal += m.optSubtotal;
    totalActualSubtotal += m.actualSubtotal;
  });

  const contingencyRate = budget?.contingency_rate ?? 0.10;
  const taxRate = budget?.tax_rate ?? 0.08;

  const optContingency = Math.round(totalOptSubtotal * contingencyRate * 100) / 100;
  const actualContingency = Math.round(totalActualSubtotal * contingencyRate * 100) / 100;

  const optTax = Math.round((totalOptSubtotal + optContingency) * taxRate * 100) / 100;
  const actualTax = Math.round((totalActualSubtotal + actualContingency) * taxRate * 100) / 100;

  const optGrandTotal = Math.round((totalOptSubtotal + optContingency + optTax) * 100) / 100;
  const actualGrandTotal = Math.round((totalActualSubtotal + actualContingency + actualTax) * 100) / 100;

  const totalSavings = Math.max(0, actualGrandTotal - optGrandTotal);
  const savingsPercent = actualGrandTotal > 0 ? Math.round((totalSavings / actualGrandTotal) * 100) : 0;

  // ATL / BTL category sums
  let atlOptSum = 0;
  let atlActualSum = 0;
  atlItems.forEach(i => {
    const m = getItemMetrics(i);
    atlOptSum += m.optSubtotal;
    atlActualSum += m.actualSubtotal;
  });

  let btlOptSum = 0;
  let btlActualSum = 0;
  btlItems.forEach(i => {
    const m = getItemMetrics(i);
    btlOptSum += m.optSubtotal;
    btlActualSum += m.actualSubtotal;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27354F] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
              Movie Magic Budgeting-Compatible
            </span>
            <span className="text-[10px] uppercase font-bold tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full">
              INR (₹) Indian Rupees
            </span>
            {showActualCost && (
              <span className="text-[10px] uppercase font-bold tracking-widest bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded-full animate-pulse">
                Actual vs. Optimised Active
              </span>
            )}
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
            Production Budget Estimation
          </h1>
          <p className="text-xs text-amber-400/90 font-medium">
            {budget?.disclaimer || 'Illustrative planning estimates — user configurable.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          {/* THE REQUESTED BUTTON: SHOW ACTUAL COST / HIDE ACTUAL COST */}
          <button
            onClick={() => setShowActualCost(!showActualCost)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md ${
              showActualCost
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-cyan-500/25 border border-cyan-400'
                : 'bg-[#1A2438] hover:bg-[#27354F] text-cyan-300 border border-cyan-500/30 hover:border-cyan-400'
            }`}
          >
            {showActualCost ? (
              <>
                <EyeOff className="w-3.5 h-3.5 text-white" />
                <span>Hide Actual Cost</span>
              </>
            ) : (
              <>
                <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                <span>Show Actual Cost</span>
              </>
            )}
          </button>

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

      {/* Comparison Banner (Appears when Show Actual Cost is clicked) */}
      {showActualCost && (
        <div className="bg-gradient-to-r from-cyan-950/40 via-[#131B2A] to-emerald-950/40 border border-cyan-500/30 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs shadow-lg animate-in fade-in duration-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">
                  Actual Market Baseline vs. AI-Optimised Production Cost
                </span>
                <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-mono px-2 py-0.5 rounded-full border border-emerald-500/40 font-bold">
                  {savingsPercent}% Cost Savings
                </span>
              </div>
              <p className="text-slate-400 text-xs mt-0.5">
                Displays unoptimised standard retail spot day-rates alongside AI schedule-batched rates (location consolidation, bulk camera & grip discounts).
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-[#0F1622] px-4 py-2 rounded-xl border border-[#222E42] shrink-0 font-mono">
            <div>
              <span className="text-[10px] text-slate-400 block uppercase">Total Cost Savings</span>
              <span className="text-emerald-400 font-extrabold text-sm">
                ₹{totalSavings.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="w-px h-7 bg-[#222E42]" />
            <div>
              <span className="text-[10px] text-slate-400 block uppercase">Efficiency</span>
              <span className="text-emerald-400 font-extrabold text-sm">
                -{savingsPercent}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Financial Summary Cards */}
      {budget && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Subtotal */}
          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex flex-col justify-between">
            <div>
              <span className="text-[11px] text-slate-400 block">
                {showActualCost ? 'Subtotal (Direct Costs)' : 'Subtotal'}
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-2xl font-black text-white font-mono">
                  ₹{totalOptSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
                {showActualCost && (
                  <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/30">
                    Optimised
                  </span>
                )}
              </div>
              {showActualCost && (
                <div className="mt-1 pt-1 border-t border-[#222E42] text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Actual Market:</span>
                  <span className="font-mono text-cyan-300 font-semibold line-through opacity-80">
                    ₹{totalActualSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
            <span className="text-[10px] text-slate-400 block mt-1">ATL + BTL Direct Costs</span>
          </div>

          {/* Card 2: Contingency */}
          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex flex-col justify-between">
            <div>
              <span className="text-[11px] text-slate-400 block">
                Contingency ({Math.round(contingencyRate * 100)}%)
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-2xl font-black text-amber-400 font-mono">
                  ₹{optContingency.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
                {showActualCost && (
                  <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/30">
                    Optimised
                  </span>
                )}
              </div>
              {showActualCost && (
                <div className="mt-1 pt-1 border-t border-[#222E42] text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Actual Contingency:</span>
                  <span className="font-mono text-amber-300/80 font-semibold line-through">
                    ₹{actualContingency.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
            <span className="text-[10px] text-slate-400 block mt-1">Unforeseen production variance</span>
          </div>

          {/* Card 3: Taxes & Permits */}
          <div className="bg-[#131B2A] border border-[#27354F] p-4 rounded-xl flex flex-col justify-between">
            <div>
              <span className="text-[11px] text-slate-400 block">
                Taxes & Permits ({Math.round(taxRate * 100)}%)
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-2xl font-black text-cyan-400 font-mono">
                  ₹{optTax.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
                {showActualCost && (
                  <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/30">
                    Optimised
                  </span>
                )}
              </div>
              {showActualCost && (
                <div className="mt-1 pt-1 border-t border-[#222E42] text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Actual Taxes:</span>
                  <span className="font-mono text-cyan-300/80 font-semibold line-through">
                    ₹{actualTax.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              )}
            </div>
            <span className="text-[10px] text-slate-400 block mt-1">Permits, insurance, tax</span>
          </div>

          {/* Card 4: Grand Total Budget */}
          <div className="bg-[#131B2A] border border-amber-500/30 p-4 rounded-xl shadow-lg bg-gradient-to-tr from-[#131B2A] to-[#1F293D] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-amber-400 font-bold block uppercase tracking-wider">
                  {showActualCost ? 'Optimised Total Cost' : 'Grand Total Budget'}
                </span>
                {showActualCost && (
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono font-bold">
                    Save {savingsPercent}%
                  </span>
                )}
              </div>
              <span className="text-2xl font-black text-white font-mono block mt-0.5">
                ₹{optGrandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>

              {showActualCost ? (
                <div className="mt-1 pt-1 border-t border-amber-500/20 space-y-0.5 text-[11px]">
                  <div className="flex items-center justify-between text-slate-300">
                    <span>Actual Market Cost:</span>
                    <span className="font-mono text-rose-300 font-bold line-through">
                      ₹{actualGrandTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-emerald-400 font-semibold">
                    <span>AI Pre-Prod Savings:</span>
                    <span className="font-mono font-bold">
                      -₹{totalSavings.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              ) : (
                <span className="text-[10px] text-emerald-400 font-medium block mt-0.5">
                  AI-Optimised Production Estimate (INR)
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Above-The-Line Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl space-y-2">
        <div className="bg-[#182235] px-6 py-3 border-b border-[#27354F] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
            <span>Above-The-Line (ATL) — Creative & Principal Talent</span>
          </span>
          <div className="flex items-center gap-3 text-xs font-mono font-bold">
            <span className="text-amber-400">
              Optimised: ₹{atlOptSum.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
            {showActualCost && (
              <span className="text-slate-400 font-normal">
                (Actual: <span className="line-through text-slate-300">₹{atlActualSum.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span> • <span className="text-emerald-400">Save ₹{(atlActualSum - atlOptSum).toLocaleString('en-IN')}</span>)
              </span>
            )}
          </div>
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
                <th className="py-2.5 px-4">
                  {showActualCost ? 'Optimised Rate (₹)' : 'Rate (₹)'}
                </th>
                {showActualCost && (
                  <th className="py-2.5 px-4 text-cyan-300">Actual Rate (₹)</th>
                )}
                <th className="py-2.5 px-4">Days</th>
                <th className="py-2.5 px-4 text-right">
                  {showActualCost ? 'Optimised (₹)' : 'Subtotal (₹)'}
                </th>
                {showActualCost && (
                  <>
                    <th className="py-2.5 px-4 text-right text-slate-400">Actual (₹)</th>
                    <th className="py-2.5 px-4 text-right text-emerald-400">Savings</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {atlItems.map((item) => {
                const m = getItemMetrics(item);
                return (
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
                    {showActualCost && (
                      <td className="py-2.5 px-4 font-mono text-cyan-300/90 font-medium">
                        ₹{m.actualRate.toLocaleString('en-IN')}
                      </td>
                    )}
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
                      ₹{m.optSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    {showActualCost && (
                      <>
                        <td className="py-2.5 px-4 text-right font-mono text-slate-300 line-through opacity-75">
                          ₹{m.actualSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="py-2.5 px-4 text-right font-mono font-bold text-emerald-400">
                          -₹{m.savings.toLocaleString('en-IN', { minimumFractionDigits: 0 })}
                        </td>
                      </>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Below-The-Line Table */}
      <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl overflow-hidden shadow-xl space-y-2">
        <div className="bg-[#182235] px-6 py-3 border-b border-[#27354F] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
            Below-The-Line (BTL) — Crew, Equipment, Locations & Post-Production
          </span>
          <div className="flex items-center gap-3 text-xs font-mono font-bold">
            <span className="text-cyan-400">
              Optimised: ₹{btlOptSum.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
            {showActualCost && (
              <span className="text-slate-400 font-normal">
                (Actual: <span className="line-through text-slate-300">₹{btlActualSum.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span> • <span className="text-emerald-400">Save ₹{(btlActualSum - btlOptSum).toLocaleString('en-IN')}</span>)
              </span>
            )}
          </div>
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
                <th className="py-2.5 px-4">
                  {showActualCost ? 'Optimised Rate (₹)' : 'Rate (₹)'}
                </th>
                {showActualCost && (
                  <th className="py-2.5 px-4 text-cyan-300">Actual Rate (₹)</th>
                )}
                <th className="py-2.5 px-4">Days</th>
                <th className="py-2.5 px-4 text-right">
                  {showActualCost ? 'Optimised (₹)' : 'Subtotal (₹)'}
                </th>
                {showActualCost && (
                  <>
                    <th className="py-2.5 px-4 text-right text-slate-400">Actual (₹)</th>
                    <th className="py-2.5 px-4 text-right text-emerald-400">Savings</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {btlItems.map((item) => {
                const m = getItemMetrics(item);
                return (
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
                    {showActualCost && (
                      <td className="py-2.5 px-4 font-mono text-cyan-300/90 font-medium">
                        ₹{m.actualRate.toLocaleString('en-IN')}
                      </td>
                    )}
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
                      ₹{m.optSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    {showActualCost && (
                      <>
                        <td className="py-2.5 px-4 text-right font-mono text-slate-300 line-through opacity-75">
                          ₹{m.actualSubtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="py-2.5 px-4 text-right font-mono font-bold text-emerald-400">
                          -₹{m.savings.toLocaleString('en-IN', { minimumFractionDigits: 0 })}
                        </td>
                      </>
                    )}
                  </tr>
                );
              })}
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
                  <label className="block text-slate-400 font-semibold mb-1">Unit Rate (₹)</label>
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
