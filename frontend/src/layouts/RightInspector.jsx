import React, { useState, useEffect } from 'react';
import { Brain, FileCode, CheckCircle2, Loader2, Info } from 'lucide-react';
import useStore from '../store';
import { api } from '../services/api';
import { useParams } from 'react-router-dom';

export function RightInspector() {
  const params = useParams();
  const [id, setId] = useState(params.id);
  const activeEntity = useStore(state => state.activeEntity);
  const setViewingFile = useStore(state => state.setViewingFile);
  const [entityDetails, setEntityDetails] = useState(null);
  const [aiResponse, setAiResponse] = useState(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    if (!params.id) {
      // fallback to grab from url or api
      const match = window.location.pathname.match(/\/repo(?:sitory)?\/([^\/]+)/);
      if (match) {
        setId(match[1]);
      } else {
        api.getRepositories().then(repos => {
          if (repos.length > 0) setId(repos[repos.length - 1].id);
        }).catch(console.error);
      }
    } else {
      setId(params.id);
    }
  }, [params.id]);

  useEffect(() => {
    if (!activeEntity || !id) {
      setEntityDetails(null);
      return;
    }

    const loadDetails = async () => {
      setLoading(true);
      try {
        const data = await api.getEntityDetails(id, activeEntity.id);
        setEntityDetails(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadDetails();
  }, [activeEntity, id]);

  const handleAsk = async (e) => {
    if (e.key === 'Enter' && query.trim() && id) {
      setAsking(true);
      try {
        const response = await api.askAI(query, id);
        // Map the backend StructuredAIResponse to what RightInspector expects
        const mappedResponse = {
          title: "CodeAtlas Expert Team",
          summary: response.analysis?.text || response.summary || "I processed your request, but couldn't generate a text response.",
          citations: []
        };
        setAiResponse(mappedResponse);
        setQuery('');
      } catch (err) {
        console.error(err);
        setAiResponse({
          title: "Error",
          summary: "Sorry, I encountered an error. Please try again."
        });
      } finally {
        setAsking(false);
      }
    }
  };

  return (
    <div className="w-80 flex flex-col bg-surface border-l border-border h-full">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-accent" />
          <span className="font-semibold text-sm">Intelligence</span>
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        
        {loading && <div className="flex justify-center py-4"><Loader2 className="w-6 h-6 animate-spin text-gray-500" /></div>}
        
        {!loading && entityDetails && (
          <div className="bg-background rounded-lg border border-border overflow-hidden">
            <div className="bg-white/5 px-3 py-2 text-xs font-medium border-b border-border uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <Info className="w-3.5 h-3.5" />
              Entity Details
            </div>
            <div className="p-3 text-sm text-gray-300 space-y-2">
              <div><span className="text-gray-500 text-xs uppercase">Name</span><br/>{entityDetails.name}</div>
              {entityDetails.type === 'file' && <div><span className="text-gray-500 text-xs uppercase">Language</span><br/>{entityDetails.language}</div>}
              {entityDetails.type === 'symbol' && <div><span className="text-gray-500 text-xs uppercase">Type</span><br/>{entityDetails.symbol_type}</div>}
              <div><span className="text-gray-500 text-xs uppercase">Risk</span><br/>
                <span className={`px-2 py-0.5 rounded text-xs mt-1 inline-block ${entityDetails.risk === 'High' ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}`}>
                  {entityDetails.risk}
                </span>
              </div>
              {(entityDetails.type === 'file' || entityDetails.type === 'symbol') && (
                <button 
                  onClick={() => {
                    const viewingEntity = {
                      id: entityDetails.type === 'symbol' ? entityDetails.file_id : entityDetails.id,
                      name: entityDetails.name
                    };
                    setViewingFile(viewingEntity);
                  }}
                  className="mt-4 w-full px-3 py-1.5 bg-primary/20 text-primary border border-primary/30 rounded text-xs font-semibold hover:bg-primary hover:text-white transition-colors"
                >
                  View Source Code
                </button>
              )}
            </div>
          </div>
        )}

        {asking && (
          <div className="bg-background rounded-lg border border-border p-4 flex items-center justify-center gap-2 text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
          </div>
        )}

        {aiResponse && !asking && (
          <>
            <div className="bg-background rounded-lg border border-border overflow-hidden">
              <div className="bg-white/5 px-3 py-2 text-xs font-medium border-b border-border uppercase tracking-wider text-gray-400">
                {aiResponse.title || aiResponse.type || "AI Response"}
              </div>
              <div className="p-3 text-sm text-gray-300">
                {aiResponse.summary}
              </div>
            </div>

            {aiResponse.citations && aiResponse.citations.length > 0 && (
              <div className="bg-background rounded-lg border border-border overflow-hidden">
                <div className="bg-white/5 px-3 py-2 text-xs font-medium border-b border-border uppercase tracking-wider text-gray-400">
                  Evidence
                </div>
                <div className="p-3 space-y-2">
                  {aiResponse.citations.map((cit, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
                      <FileCode className="w-3.5 h-3.5 text-gray-500" />
                      <span className="truncate">{cit.file_path || cit.name || "Unknown"}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {!activeEntity && !aiResponse && !loading && (
          <div className="text-center text-gray-500 text-sm mt-10">
            Select a node in the graph or ask a question below to begin exploration.
          </div>
        )}

      </div>
      
      <div className="p-4 border-t border-border">
        <input 
          type="text" 
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleAsk}
          placeholder="Ask Repository..." 
          className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-accent text-gray-200"
          disabled={asking}
        />
      </div>
    </div>
  )
}
