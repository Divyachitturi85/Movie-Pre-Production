import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const projectService = {
  list: () => api.get('/projects').then(res => res.data),
  create: (data) => api.post('/projects', data).then(res => res.data),
  get: (id) => api.get(`/projects/${id}`).then(res => res.data),
  delete: (id) => api.delete(`/projects/${id}`).then(res => res.data),
  loadDemo: () => api.post('/projects/demo/load').then(res => res.data),
};

export const scriptService = {
  upload: (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/projects/${projectId}/script/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data);
  },
  get: (projectId) => api.get(`/projects/${projectId}/script`).then(res => res.data),
  parse: (projectId, rawText) => api.post(`/projects/${projectId}/script/parse`, { raw_text: rawText }).then(res => res.data),
};

export const analysisService = {
  runAnalysis: (projectId) => api.post(`/projects/${projectId}/analyze`).then(res => res.data),
  getScenes: (projectId) => api.get(`/projects/${projectId}/scenes`).then(res => res.data),
  getScene: (projectId, sceneId) => api.get(`/projects/${projectId}/scenes/${sceneId}`).then(res => res.data),
  getCharacters: (projectId) => api.get(`/projects/${projectId}/characters`).then(res => res.data),
  updateCharacter: (projectId, charId, data) => api.put(`/projects/${projectId}/characters/${charId}`, data).then(res => res.data),
  getLocations: (projectId) => api.get(`/projects/${projectId}/locations`).then(res => res.data),
  getElements: (projectId, category) => api.get(`/projects/${projectId}/elements`, { params: { category } }).then(res => res.data),
  createElement: (projectId, data) => api.post(`/projects/${projectId}/elements`, data).then(res => res.data),
  deleteElement: (projectId, elementId) => api.delete(`/projects/${projectId}/elements/${elementId}`).then(res => res.data),
};

export const scheduleService = {
  optimize: (projectId, params = {}) => api.post(`/projects/${projectId}/schedule/optimize`, params).then(res => res.data),
  get: (projectId) => api.get(`/projects/${projectId}/schedule`).then(res => res.data),
  getStripboard: (projectId) => api.get(`/projects/${projectId}/stripboard`).then(res => res.data),
};

export const budgetService = {
  get: (projectId) => api.get(`/projects/${projectId}/budget`).then(res => res.data),
  generate: (projectId) => api.post(`/projects/${projectId}/budget/generate`).then(res => res.data),
  updateItems: (projectId, items) => api.put(`/projects/${projectId}/budget/items`, items).then(res => res.data),
  updateConfig: (projectId, config) => api.put(`/projects/${projectId}/budget/config`, config).then(res => res.data),
};

export const documentService = {
  getCallSheets: (projectId) => api.get(`/projects/${projectId}/call-sheets`).then(res => res.data),
  generateCallSheets: (projectId) => api.post(`/projects/${projectId}/call-sheets/generate`).then(res => res.data),
  getCallbacks: (projectId) => api.get(`/projects/${projectId}/callbacks`).then(res => res.data),
  generateCallbacks: (projectId) => api.post(`/projects/${projectId}/callbacks/generate`).then(res => res.data),
  createCallback: (projectId, data) => api.post(`/projects/${projectId}/callbacks/single`, data).then(res => res.data),
  getReport: (projectId) => api.get(`/projects/${projectId}/reports`).then(res => res.data),
  getExplainability: (projectId, stage) => api.get(`/projects/${projectId}/explainability`, { params: { stage } }).then(res => res.data),
  
  // Direct download URLs
  getPackageDownloadUrl: (projectId) => `/api/projects/${projectId}/export/package`,
  getCallSheetPdfUrl: (projectId, sheetId) => `/api/projects/${projectId}/call-sheets/${sheetId}/export/pdf`,
  getCallSheetDocxUrl: (projectId, sheetId) => `/api/projects/${projectId}/call-sheets/${sheetId}/export/docx`,
  getCallbacksPdfUrl: (projectId) => `/api/projects/${projectId}/callbacks/export/pdf`,
};

export default api;
