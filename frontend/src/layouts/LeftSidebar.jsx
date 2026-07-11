import React, { useState, useEffect } from 'react'
import { FolderGit2, Search, Settings, Loader2, Home, Network, AlertTriangle } from 'lucide-react'
import { api } from '../services/api'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import useStore from '../store'

export function LeftSidebar() {
  const [repos, setRepos] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const setActiveEntity = useStore(state => state.setActiveEntity);

  useEffect(() => {
    api.getRepositories().then(setRepos).catch(console.error);
  }, []);

  useEffect(() => {
    if (!searchQuery) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const activeRepo = repos.length > 0 ? repos[repos.length - 1].id : null;
        if (activeRepo) {
          const results = await api.searchRepository(activeRepo, searchQuery);
          setSearchResults(results);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setIsSearching(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, repos]);

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
            onClick={() => navigate(`/repo/${id}/flow`)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              location.pathname.startsWith(`/repo/${id}/flow`)
                ? 'bg-primary/20 text-primary'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Network className="w-4 h-4" />
            Graph Explorer
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
          <div className="mt-4">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Search Results</div>
            <ul className="space-y-1 overflow-y-auto max-h-60">
              {isSearching ? (
                <li className="px-3 py-2 flex items-center justify-center"><Loader2 className="w-4 h-4 animate-spin text-gray-500" /></li>
              ) : searchResults.length === 0 ? (
                <li className="px-3 py-2 text-gray-500 text-sm">No results found</li>
              ) : (
                searchResults.map(res => (
                  <li key={res.id} onClick={() => { setActiveEntity(res); navigate(`/repo/${repos[repos.length - 1].id}/flow`); }} className="px-3 py-2 rounded-md text-xs cursor-pointer hover:bg-white/10 transition-colors flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${res.type === 'file' ? 'bg-blue-500' : 'bg-purple-500'}`}></span>
                    <span className="truncate" title={res.name}>{res.name.split('/').pop()}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
        ) : (
          <>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 mt-6">Repositories</div>
            <ul className="space-y-1 overflow-y-auto max-h-60">
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
          </>
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
