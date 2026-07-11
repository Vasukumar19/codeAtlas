const BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  importRepository: async (url) => {
    const res = await fetch(`${BASE_URL}/repositories/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    if (!res.ok) throw new Error('Import failed');
    return res.json(); // returns { job_id, message }
  },
  
  getRepositories: async () => {
    const res = await fetch(`${BASE_URL}/repositories/`);
    if (!res.ok) throw new Error('Failed to fetch repositories');
    return res.json();
  },

  getRepository: async (id) => {
    const res = await fetch(`${BASE_URL}/repositories/${id}`);
    if (!res.ok) throw new Error('Failed to fetch repository');
    return res.json();
  },

  getRepositoryStatus: async (id) => {
    const res = await fetch(`${BASE_URL}/repositories/${id}/status`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  fetchRepositoryStats: async (repoId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },
  
  askAI: async (query, repoId) => {
    const res = await fetch(`${BASE_URL}/intelligence/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, repository_id: repoId })
    });
    if (!res.ok) throw new Error('Failed to fetch AI response');
    return res.json();
  },

  getGraph: async (repoId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/graph`);
    if (!res.ok) throw new Error('Failed to fetch graph');
    return res.json();
  },

  getEntityDetails: async (repoId, entityId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/entities/${entityId}`);
    if (!res.ok) throw new Error('Failed to fetch entity details');
    return res.json();
  },

  getFileContent: async (repoId, fileId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/files/${fileId}/content`);
    if (!res.ok) throw new Error('Failed to fetch file content');
    return res.json();
  },

  searchRepository: async (repoId, query) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to search');
    return res.json();
  },

  getHotFiles: async (repoId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/hot-files`);
    if (!res.ok) throw new Error('Failed to fetch hot files');
    return res.json();
  },

  getImpactAnalysis: async (repoId, entityId, hops = 3) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/impact/${entityId}?hops=${hops}`);
    if (!res.ok) throw new Error('Failed to fetch impact analysis');
    return res.json();
  },

  getExecutionFlow: async (repoId, entityId) => {
    const suffix = entityId ? `?entity_id=${entityId}` : '';
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/execution-flow${suffix}`);
    if (!res.ok) throw new Error('Failed to fetch execution flow');
    return res.json();
  },

  getSecurityFindings: async (repoId) => {
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/security-findings`);
    if (!res.ok) throw new Error('Failed to fetch security findings');
    return res.json();
  },

  generateDocs: async (repoId, path) => {
    const suffix = path ? `?path=${encodeURIComponent(path)}` : '';
    const res = await fetch(`${BASE_URL}/repositories/${repoId}/docs${suffix}`);
    if (!res.ok) throw new Error('Failed to generate documentation draft');
    return res.json();
  }
};
