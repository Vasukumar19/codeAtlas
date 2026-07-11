import React, { useState, useEffect } from 'react'
import { FolderGit2, Search, Settings, Loader2, Home, Network, AlertTriangle, Cpu, FileCode, Code2, Globe, ListTodo, History } from 'lucide-react'
import { api } from '../services/api'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import useStore from '../store'

export function LeftSidebar() {
  const [repos, setRepos] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const setActiveEntity = useStore(state => state.setActiveEntity);

  useEffect(() => {
    api.getRepositories().then(setRepos).catch(console.error);
  }, []);

  const activeRepoId = id || (repos.length > 0 ? repos[repos.length - 1].id : null);

  useEffect(() => {
    if (!activeRepoId) return;
    const stored = localStorage.getItem(`codeatlas_recent_${activeRepoId}`);
    if (stored) {
      try {
        setRecentSearches(JSON.parse(stored));
      } catch (e) {
        console.error(e);
      }
    }
  }, [activeRepoId]);

  const saveRecentSearch = (queryStr) => {
    if (!queryStr || !activeRepoId) return;
    const clean = queryStr.trim();
    if (!clean) return;
    setRecentSearches(prev => {
      const filtered = prev.filter(q => q !== clean);
      const updated = [clean, ...filtered].slice(0, 5);
      localStorage.setItem(`codeatlas_recent_${activeRepoId}`, JSON.stringify(updated));
      return updated;
    });
  };

  useEffect(() => {
    if (!searchQuery) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        if (activeRepoId) {
          const results = await api.searchRepository(activeRepoId, searchQuery);
          setSearchResults(results);
          saveRecentSearch(searchQuery);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setIsSearching(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, activeRepoId]);

  const groupedResults = useMemo(() => {
    const groups = { file: [], symbol: [], route: [], todo: [] };
    searchResults.forEach(res => {
      const type = res.type || 'symbol';
      if (!groups[type]) groups[type] = [];
      groups[type].push(res);
    });
    return groups;
  }, [searchResults]);

  return (
    <div className="w-64 flex flex-col bg-surface border-r border-border h-full p-4">
      <div className="flex items-center gap-2 mb-8 text-primary">
        <FolderGit2 className="w-6 h-6" />
        <span className="font-bold text-xl tracking-tight text-white">CodeAtlas</span>
      </div>

      {id && (
        <div className="mb-6 space-y-1">
          <button
            onClick={() => navigate(`/repo/${id}`)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              location.pathname === `/repo/${id}`
                ? 'bg-primary/20 text-primary'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Home className="w-4 h-4" />
            Dashboard
          </button>
          <button
            onClick={() => navigate(`/repo/${id}/graph`)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              location.pathname.startsWith(`/repo/${id}/graph`)
                ? 'bg-primary/20 text-primary'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Network className="w-4 h-4" />
            Graph Explorer
          </button>
          <button
            onClick={() => navigate(`/repo/${id}/flow`)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              location.pathname.startsWith(`/repo/${id}/flow`)
                ? 'bg-primary/20 text-primary'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Cpu className="w-4 h-4" />
            Execution Flow
          </button>
          <button
            onClick={() => navigate(`/repo/${id}/analysis`)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              location.pathname.startsWith(`/repo/${id}/analysis`)
                ? 'bg-primary/20 text-primary'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            Analysis
          </button>
        </div>
      )}
      
      <div className="flex-1 flex flex-col min-h-0">
        <div className="relative mb-6">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search everything..." 
            className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-primary text-gray-200"
          />
        </div>
        
        {searchQuery ? (
          <div className="mt-4 flex-1 flex flex-col min-h-0 overflow-y-auto">
            <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2 px-2">Search Results</div>
            {isSearching ? (
              <div className="px-3 py-2 flex items-center justify-center"><Loader2 className="w-4 h-4 animate-spin text-gray-500" /></div>
            ) : searchResults.length === 0 ? (
              <div className="px-3 py-2 text-gray-500 text-xs">No results found</div>
            ) : (
              <div className="space-y-3">
                {Object.keys(groupedResults).map(groupName => {
                  const items = groupedResults[groupName];
                  if (items.length === 0) return null;
                  return (
                    <div key={groupName} className="space-y-1">
                      <div className="text-[9px] font-bold text-gray-500 uppercase tracking-wider px-2">{groupName}s</div>
                      <ul className="space-y-0.5">
                        {items.map(res => (
                          <li 
                            key={res.id} 
                            onClick={() => { 
                              setActiveEntity(res); 
                              navigate(`/repo/${activeRepoId}/graph`); 
                            }} 
                            className="px-3 py-1.5 rounded-md text-xs cursor-pointer hover:bg-white/5 transition-colors flex items-center gap-2 text-gray-300 hover:text-white"
                          >
                            {res.type === 'file' && <FileCode className="w-3.5 h-3.5 text-blue-400 shrink-0" />}
                            {res.type === 'symbol' && <Code2 className="w-3.5 h-3.5 text-purple-400 shrink-0" />}
                            {res.type === 'route' && <Globe className="w-3.5 h-3.5 text-green-400 shrink-0" />}
                            {res.type === 'todo' && <ListTodo className="w-3.5 h-3.5 text-yellow-400 shrink-0" />}
                            <span className="truncate" title={res.name}>{res.name.split('/').pop()}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
            {recentSearches.length > 0 && (
              <div className="mb-4">
                <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2 px-2">Recent Searches</div>
                <ul className="space-y-0.5">
                  {recentSearches.map(q => (
                    <li
                      key={q}
                      onClick={() => setSearchQuery(q)}
                      className="px-3 py-1.5 rounded-md text-xs text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer flex items-center gap-2 transition-colors"
                    >
                      <History className="w-3.5 h-3.5 text-gray-500 shrink-0" />
                      <span className="truncate">{q}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2 px-2">Repositories</div>
            <ul className="space-y-1">
              {repos.length === 0 ? (
                <li className="px-3 py-2 flex items-center justify-center"><Loader2 className="w-4 h-4 animate-spin text-gray-500" /></li>
              ) : (
                repos.map(r => (
                  <li key={r.id} onClick={() => navigate(`/repo/${r.id}`)} className="px-3 py-2 rounded-md text-sm cursor-pointer hover:bg-white/10 transition-colors flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    <span className="truncate">{r.name}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>
      
      <div 
        onClick={() => navigate(id ? `/repo/${id}/settings` : '/settings')}
        className={`pt-4 border-t border-border mt-auto flex items-center gap-2 cursor-pointer transition-colors ${
          location.pathname.includes('/settings')
            ? 'text-primary'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <Settings className="w-4 h-4" />
        <span className="text-sm">Settings</span>
      </div>
    </div>
  )
}
