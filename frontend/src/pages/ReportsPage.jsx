import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Download,
  FileCheck2,
  FileSpreadsheet,
  FileText,
  Mail,
  Layers,
  Calendar,
  CreditCard,
  Archive,
  ShieldCheck,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { documentService } from '../services/api';

const PACKAGE_DOCS = [
  { name: '01_Script_Breakdown.pdf', label: 'Script Breakdown Sheet', type: 'PDF', icon: Layers, desc: 'Scene-by-scene breakdown of all required production elements.' },
  { name: '02_Scene_Breakdown.xlsx', label: 'Scene Data Ledger', type: 'XLSX', icon: FileSpreadsheet, desc: 'Tabular scene data, duration, page counts, and complexity.' },
  { name: '03_Cast_Breakdown.xlsx', label: 'Cast & Character Ledger', type: 'XLSX', icon: FileSpreadsheet, desc: 'Actor roles, dialogue counts, screen time, and required shoot days.' },
  { name: '04_Location_Breakdown.xlsx', label: 'Location & Sets Ledger', type: 'XLSX', icon: FileSpreadsheet, desc: 'INT/EXT categorization, days required, and company moves.' },
  { name: '05_Production_Elements.xlsx', label: 'Production Elements Inventory', type: 'XLSX', icon: FileSpreadsheet, desc: 'Inventory of props, costumes, vehicles, VFX/SFX, and equipment.' },
  { name: '06_Shooting_Schedule.xlsx', label: 'OR-Tools Shooting Schedule', type: 'XLSX', icon: FileSpreadsheet, desc: 'Day-by-day shoot sequence with start times and turnaround buffer.' },
  { name: '07_Stripboard.pdf', label: 'Movie Magic Stripboard', type: 'PDF', icon: FileText, desc: 'Industry standard color-coded physical stripboard representation.' },
  { name: '08_Budget.xlsx', label: 'Production Budget Ledger', type: 'XLSX', icon: FileSpreadsheet, desc: 'Above-the-Line & Below-the-Line budget with tax and contingency.' },
  { name: '09_Call_Sheets.pdf', label: 'StudioBinder Call Sheets', type: 'PDF', icon: FileCheck2, desc: 'Daily official call sheets for every shooting day.' },
  { name: '10_Callback_Letters.pdf', label: 'Talent Callback Letters', type: 'PDF', icon: Mail, desc: 'Formal talent audition callback letters with appointment slots.' },
  { name: '11_Pre_Production_Report.pdf', label: 'Executive Pre-Production Report', type: 'PDF', icon: FileText, desc: 'Comprehensive executive briefing and AI pipeline audit.' },
  { name: 'complete_project.json', label: 'Complete Project JSON', type: 'JSON', icon: Archive, desc: 'Full database export of all project entities and relationships.' },
];

export default function ReportsPage() {
  const { currentProject } = useOutletContext();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!currentProject?.id) return;
    loadReport();
  }, [currentProject?.id]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const data = await documentService.getReport(currentProject.id);
      setReport(data);
    } catch (err) {
      console.error('Failed to load report:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadPackageUrl = documentService.getPackageDownloadUrl(currentProject?.id);

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#182235] via-[#1C283F] to-[#121927] border border-[#27354F] rounded-2xl p-6 sm:p-8 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] uppercase font-bold tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Production Dossier
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Final Pre-Production Package & Exports
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-xl leading-relaxed">
            Download the complete compiled production bundle containing all 11 industry-standard production artifacts,
            spreadsheets, PDF documents, and JSON database export.
          </p>
        </div>

        <a
          href={downloadPackageUrl}
          download
          className="flex items-center justify-center gap-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black px-6 py-3.5 rounded-xl text-xs sm:text-sm shadow-xl shadow-amber-500/25 transition active:scale-95 shrink-0"
        >
          <Download className="w-5 h-5 stroke-[2.5]" />
          <span>Download Complete Package (.ZIP)</span>
        </a>
      </div>

      {/* Package Contents Grid */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Archive className="w-4 h-4 text-amber-400" />
          <span>Package Artifacts (11 Documents + JSON Export)</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {PACKAGE_DOCS.map((doc, idx) => {
            const Icon = doc.icon;
            return (
              <div
                key={idx}
                className="bg-[#131B2A] border border-[#27354F] rounded-xl p-4 flex items-start gap-3.5 hover:border-slate-600 transition shadow-sm"
              >
                <div className="w-9 h-9 rounded-lg bg-[#182235] border border-[#27354F] flex items-center justify-center text-amber-400 shrink-0">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-xs text-white truncate">{doc.name}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                      doc.type === 'PDF' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                      doc.type === 'XLSX' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                      'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    }`}>
                      {doc.type}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{doc.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Executive Briefing Summary */}
      {report && (
        <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
          <div className="border-b border-[#222E42] pb-4">
            <h3 className="text-base font-bold text-white">Pre-Production Executive Briefing</h3>
            <p className="text-xs text-slate-400 mt-0.5">Automated story and logistical summary for key stakeholders</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
              <span className="text-slate-400 text-[11px] block">Total Scenes</span>
              <span className="text-lg font-bold text-white">{report.statistics?.total_scenes}</span>
            </div>
            <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
              <span className="text-slate-400 text-[11px] block">Characters</span>
              <span className="text-lg font-bold text-cyan-400">{report.statistics?.total_characters}</span>
            </div>
            <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
              <span className="text-slate-400 text-[11px] block">Optimized Shoot Days</span>
              <span className="text-lg font-bold text-emerald-400">{report.schedule_summary?.total_days} days</span>
            </div>
            <div className="bg-[#182235] p-3.5 rounded-xl border border-[#222E42]">
              <span className="text-slate-400 text-[11px] block">Grand Total Budget</span>
              <span className="text-lg font-bold text-amber-400 font-mono">
                ${report.budget_summary?.grand_total?.toLocaleString()}
              </span>
            </div>
          </div>

          {/* AI Tools & Methodologies Breakdown */}
          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">AI Engineering Methodologies</h4>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-[#182235] border border-[#222E42] flex items-center justify-between">
                <div>
                  <span className="font-bold text-white">Optical Text Extraction: </span>
                  <span className="text-slate-400">PyMuPDF digital parser with automated PaddleOCR fallback for scanned pages.</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 font-bold">PyMuPDF + PaddleOCR</span>
              </div>
              <div className="p-3 rounded-xl bg-[#182235] border border-[#222E42] flex items-center justify-between">
                <div>
                  <span className="font-bold text-white">Semantic Asset & NER Extraction: </span>
                  <span className="text-slate-400">Hugging Face BERT-NER token classification combined with spaCy noun chunks.</span>
                </div>
                <span className="text-[10px] font-mono text-cyan-400 font-bold">BERT + spaCy</span>
              </div>
              <div className="p-3 rounded-xl bg-[#182235] border border-[#222E42] flex items-center justify-between">
                <div>
                  <span className="font-bold text-white">Schedule Optimization Engine: </span>
                  <span className="text-slate-400">Google OR-Tools CP-SAT multi-objective integer programming model.</span>
                </div>
                <span className="text-[10px] font-mono text-amber-400 font-bold">OR-Tools CP-SAT</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
