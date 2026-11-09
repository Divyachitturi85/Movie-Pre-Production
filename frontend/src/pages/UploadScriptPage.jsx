import React, { useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  Cpu,
  Layers,
  Eye,
  FileCode,
  ArrowRight
} from 'lucide-react';
import { scriptService, analysisService } from '../services/api';

export default function UploadScriptPage() {
  const { currentProject, loadProjects } = useOutletContext();
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [scriptInfo, setScriptInfo] = useState(null);
  const [error, setError] = useState(null);
  const [pastedText, setPastedText] = useState('');
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'paste'

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a valid .pdf file.');
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!currentProject?.id) {
      setError('No active project selected. Please select or create a project from the top bar before uploading a screenplay.');
      return;
    }
    if (!file) {
      setError('Please select a screenplay PDF file to upload.');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const res = await scriptService.upload(currentProject.id, file);
      setScriptInfo(res);
      await loadProjects();
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Failed to upload and parse PDF.');
    } finally {
      setUploading(false);
    }
  };

  const handleParsePasted = async () => {
    if (!currentProject?.id) {
      setError('No active project selected. Please select or create a project from the top bar before parsing screenplay text.');
      return;
    }
    if (!pastedText.trim()) {
      setError('Please paste screenplay text to parse.');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const res = await scriptService.parse(currentProject.id, pastedText);
      setScriptInfo(res);
      await loadProjects();
    } catch (err) {
      console.error('Parse failed:', err);
      setError(err.response?.data?.detail || 'Failed to parse screenplay text.');
    } finally {
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!currentProject?.id) {
      setError('No active project selected. Please select or create a project.');
      return;
    }
    setAnalyzing(true);
    try {
      await analysisService.runAnalysis(currentProject.id);
      await loadProjects();
      navigate('/breakdown');
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.response?.data?.detail || 'Failed to complete NLP analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Screenplay PDF Ingestion & OCR</h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload any feature or short movie script PDF. Our engine evaluates digital text quality and triggers
          PaddleOCR if scanned pages are detected, automatically generating scene breakdown sheets and full shoot equipment packages.
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex border-b border-[#27354F]">
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex items-center gap-2 px-6 py-3 text-xs font-bold border-b-2 transition ${
            activeTab === 'upload'
              ? 'border-amber-500 text-amber-400 bg-amber-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-4 h-4" />
          <span>Upload PDF Screenplay</span>
        </button>
        <button
          onClick={() => setActiveTab('paste')}
          className={`flex items-center gap-2 px-6 py-3 text-xs font-bold border-b-2 transition ${
            activeTab === 'paste'
              ? 'border-amber-500 text-amber-400 bg-amber-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileCode className="w-4 h-4" />
          <span>Paste Screenplay Text</span>
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 flex items-center gap-3 text-rose-400 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {activeTab === 'upload' ? (
        /* PDF Drag & Drop Area */
        <div className="bg-[#131B2A] border-2 border-dashed border-[#27354F] hover:border-amber-500/50 rounded-2xl p-8 text-center transition">
          <input
            type="file"
            id="pdf-upload"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          <label htmlFor="pdf-upload" className="cursor-pointer space-y-4 block">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Upload className="w-7 h-7" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">
                {file ? file.name : 'Select or drag & drop movie screenplay PDF'}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports Standard Industry Screenplay PDF, Scanned / Physical OCR Documents
              </p>
            </div>
          </label>

          <div className="mt-6 flex justify-center">
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-xs transition shadow-lg shadow-amber-500/20"
            >
              {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>{uploading ? 'Processing PDF & Extracting Equipment...' : 'Upload & Generate Script Breakdown'}</span>
            </button>
          </div>
        </div>
      ) : (
        /* Text Paste Area */
        <div className="space-y-4">
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Paste raw screenplay text here (e.g., INT. WAREHOUSE - NIGHT)..."
            rows={12}
            className="w-full bg-[#131B2A] border border-[#27354F] rounded-2xl p-4 text-xs font-screenplay text-slate-200 focus:outline-none focus:border-amber-500"
          />
          <div className="flex justify-end">
            <button
              onClick={handleParsePasted}
              disabled={!pastedText.trim() || uploading}
              className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-xs transition"
            >
              {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              <span>Parse & Extract Production Elements</span>
            </button>
          </div>
        </div>
      )}

      {/* Script Ingestion Result Card */}
      {scriptInfo && (
        <div className="bg-[#131B2A] border border-emerald-500/30 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">{scriptInfo.filename}</h3>
                <p className="text-xs text-slate-400">Parsed into scenes & shoot equipment packages auto-generated</p>
              </div>
            </div>

            <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
              {scriptInfo.extraction_method} ({Math.round(scriptInfo.ocr_confidence * 100)}% Confidence)
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="bg-[#182235] p-3 rounded-xl border border-[#27354F]">
              <span className="text-slate-400 block text-[11px]">Pages</span>
              <span className="text-white font-bold text-base">{scriptInfo.page_count}</span>
            </div>
            <div className="bg-[#182235] p-3 rounded-xl border border-[#27354F]">
              <span className="text-slate-400 block text-[11px]">Method</span>
              <span className="text-white font-bold text-sm font-mono">{scriptInfo.extraction_method}</span>
            </div>
            <div className="bg-[#182235] p-3 rounded-xl border border-[#27354F]">
              <span className="text-slate-400 block text-[11px]">OCR Confidence</span>
              <span className="text-emerald-400 font-bold text-base">{Math.round(scriptInfo.ocr_confidence * 100)}%</span>
            </div>
            <div className="bg-[#182235] p-3 rounded-xl border border-[#27354F]">
              <span className="text-slate-400 block text-[11px]">Raw Characters</span>
              <span className="text-white font-bold text-base">{scriptInfo.raw_text?.length || 0}</span>
            </div>
          </div>

          {/* Action Trigger for Next Stage */}
          <div className="pt-2 flex flex-wrap gap-3 justify-end items-center">
            <button
              onClick={() => navigate('/script-viewer')}
              className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-300 px-4 py-2 rounded-xl text-xs font-semibold border border-[#27354F] transition"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Read in Script Viewer</span>
            </button>

            <button
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="flex items-center gap-2 bg-[#1A2438] hover:bg-[#27354F] text-slate-300 px-4 py-2 rounded-xl text-xs font-semibold border border-[#27354F] transition disabled:opacity-50"
            >
              {analyzing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Cpu className="w-3.5 h-3.5 text-amber-400" />}
              <span>{analyzing ? 'Re-analyzing...' : 'Re-Run NLP Breakdown'}</span>
            </button>

            <button
              onClick={() => navigate('/breakdown')}
              className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 px-5 py-2 rounded-xl text-xs font-bold transition shadow-lg shadow-amber-500/20"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>View Script Breakdown Sheets</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
