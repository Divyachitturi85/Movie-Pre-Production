import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import UploadScriptPage from './pages/UploadScriptPage';
import ScriptViewerPage from './pages/ScriptViewerPage';
import ScriptBreakdownPage from './pages/ScriptBreakdownPage';
import CharactersPage from './pages/CharactersPage';
import LocationsPage from './pages/LocationsPage';
import ProductionElementsPage from './pages/ProductionElementsPage';
import SchedulePage from './pages/SchedulePage';
import StripboardPage from './pages/StripboardPage';
import BudgetPage from './pages/BudgetPage';
import CallSheetsPage from './pages/CallSheetsPage';
import CallbackLettersPage from './pages/CallbackLettersPage';
import ReportsPage from './pages/ReportsPage';
import ExplainabilityPage from './pages/ExplainabilityPage';
import { projectService } from './services/api';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadProjects = async () => {
    try {
      const list = await projectService.list();
      setProjects(list);
      if (list.length > 0) {
        // Keep current project or select first
        setCurrentProject(prev => {
          if (prev) {
            const found = list.find(p => p.id === prev.id);
            return found || list[0];
          }
          return list[0];
        });
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <AppLayout
              currentProject={currentProject}
              setCurrentProject={setCurrentProject}
              projects={projects}
              loadProjects={loadProjects}
            />
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadScriptPage />} />
          <Route path="/script-viewer" element={<ScriptViewerPage />} />
          <Route path="/breakdown" element={<ScriptBreakdownPage />} />
          <Route path="/characters" element={<CharactersPage />} />
          <Route path="/locations" element={<LocationsPage />} />
          <Route path="/elements" element={<ProductionElementsPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/stripboard" element={<StripboardPage />} />
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/call-sheets" element={<CallSheetsPage />} />
          <Route path="/callbacks" element={<CallbackLettersPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/explainability" element={<ExplainabilityPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
