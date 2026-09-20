import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Film,
  Upload,
  BookOpen,
  Layers,
  Users,
  MapPin,
  Package,
  Calendar,
  CreditCard,
  FileSpreadsheet,
  Mail,
  FileCheck2,
  Cpu,
  Sparkles,
  ChevronRight,
  Plus,
  RefreshCw,
  FolderOpen
} from 'lucide-react';
import { projectService } from '../services/api';

const navItems = [
  { to: '/', label: 'Dashboard', icon: Film },
  { to: '/upload', label: 'Upload Script', icon: Upload },
  { to: '/script-viewer', label: 'Script Viewer', icon: BookOpen },
  { to: '/breakdown', label: 'Script Breakdown', icon: Layers },
  { to: '/characters', label: 'Characters & Cast', icon: Users },
  { to: '/locations', label: 'Locations & Sets', icon: MapPin },
  { to: '/elements', label: 'Production Elements', icon: Package },
  { to: '/schedule', label: 'OR-Tools Schedule', icon: Calendar },
  { to: '/stripboard', label: 'Movie Magic Stripboard', icon: FileSpreadsheet },
  { to: '/budget', label: 'Production Budget', icon: CreditCard },
  { to: '/call-sheets', label: 'Call Sheets', icon: FileCheck2 },
  { to: '/callbacks', label: 'Callback Letters', icon: Mail },
  { to: '/reports', label: 'Package & Reports', icon: Film },
  { to: '/explainability', label: 'AI Explainability', icon: Cpu },
];

export default function AppLayout({ currentProject, setCurrentProject, projects, loadProjects }) {
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [newProjName, setNewProjName] = useState('');
  const [newProjGenre, setNewProjGenre] = useState('Sci-Fi / Action Thriller');
  const navigate = useNavigate();
  const location = useLocation();

  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    try {
      const demo = await projectService.loadDemo();
      await loadProjects();
      setCurrentProject(demo);
      navigate('/');
    } catch (err) {
      console.error('Failed to load demo project:', err);
      alert('Error loading demo project: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoadingDemo(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProjName.trim()) return;
    try {
      const created = await projectService.create({
        name: newProjName,
        genre: newProjGenre,
        director: 'TBD',
        producer: 'TBD'
      });
      await loadProjects();
      setCurrentProject(created);
      setShowNewModal(false);
      setNewProjName('');
      navigate('/upload');
    } catch (err) {
      console.error('Failed to create project:', err);
      alert('Error creating project: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="h-16 bg-[#131B2A] border-b border-[#27354F] px-6 flex items-center justify-between sticky top-0 z-30 shadow-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 via-amber-500 to-yellow-400 flex items-center justify-center shadow-lg shadow-amber-500/20 text-slate-950 font-black">
              <Film className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white">CINEPLAN AI</span>
                <span className="text-[10px] uppercase font-bold tracking-widest bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                  Studio Edition
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Pre-Production & Production Management Engine</p>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-800 mx-2 hidden md:block" />

          {/* Project Switcher */}
          <div className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4 text-slate-400 hidden sm:block" />
            <select
              value={currentProject?.id || ''}
              onChange={(e) => {
                const p = projects.find(x => x.id === parseInt(e.target.value));
                if (p) setCurrentProject(p);
              }}
              className="bg-[#1A2438] text-slate-200 text-xs rounded-lg px-3 py-1.5 border border-[#27354F] focus:outline-none focus:border-amber-500 font-medium"
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.status})
                </option>
              ))}
            </select>
            <button
              onClick={() => setShowNewModal(true)}
              className="p-1.5 rounded-lg bg-[#1A2438] hover:bg-[#27354F] text-slate-300 transition text-xs flex items-center gap-1 border border-[#27354F]"
              title="Create New Project"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New</span>
            </button>
          </div>
        </div>

        {/* Action button: Demo Project */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleLoadDemo}
            disabled={loadingDemo}
            className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-3.5 py-1.5 rounded-lg text-xs shadow-md shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-50"
          >
            {loadingDemo ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>Load Demo Project (Project Aurora)</span>
          </button>
        </div>
      </header>

      {/* Main App Container */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-[#111724] border-r border-[#222E42] flex flex-col shrink-0 overflow-y-auto">
          <div className="p-4 border-b border-[#222E42]">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Current Production</div>
            <div className="bg-[#182235] p-3 rounded-xl border border-[#27354F]">
              <div className="font-bold text-sm text-white truncate">{currentProject?.name || 'No Project'}</div>
              <div className="text-xs text-amber-400/90 font-medium mt-0.5">{currentProject?.genre || 'Screenplay'}</div>
              <div className="flex items-center gap-3 mt-2 text-[11px] text-slate-400">
                <span>{currentProject?.scene_count || 0} Scenes</span>
                <span>•</span>
                <span>{currentProject?.total_shooting_days || 0} Shoot Days</span>
              </div>
            </div>
          </div>

          <nav className="p-3 space-y-1 flex-1">
            <div className="px-3 py-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Navigation Workflow</div>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20 font-bold'
                        : 'text-slate-300 hover:bg-[#1A2438] hover:text-white'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* AI Engines Operational Badge */}
          <div className="p-3 border-t border-[#222E42] bg-[#0E1420]">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>Active AI Pipeline</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>
            <div className="space-y-1 text-[11px] text-slate-400">
              <div className="flex justify-between">
                <span>OCR:</span>
                <span className="text-slate-300 font-mono">PaddleOCR v3.7</span>
              </div>
              <div className="flex justify-between">
                <span>NLP:</span>
                <span className="text-slate-300 font-mono">BERT + spaCy</span>
              </div>
              <div className="flex justify-between">
                <span>Schedule:</span>
                <span className="text-emerald-400 font-mono">OR-Tools CP-SAT</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <main className="flex-1 bg-[#0B0F17] overflow-y-auto p-6 md:p-8">
          <Outlet context={{ currentProject, setCurrentProject, loadProjects }} />
        </main>
      </div>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#131B2A] border border-[#27354F] rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Create New Production</h3>
            <p className="text-xs text-slate-400 mb-4">Initialize a new screenplay production workspace.</p>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Project Name</label>
                <input
                  type="text"
                  value={newProjName}
                  onChange={(e) => setNewProjName(e.target.value)}
                  placeholder="e.g. Neon Horizon"
                  required
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Genre</label>
                <input
                  type="text"
                  value={newProjGenre}
                  onChange={(e) => setNewProjGenre(e.target.value)}
                  placeholder="e.g. Sci-Fi Thriller / Action"
                  className="w-full bg-[#1A2438] border border-[#27354F] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 rounded-lg bg-[#1A2438] hover:bg-[#27354F] text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold shadow-md shadow-amber-500/20"
                >
                  Create & Upload
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
