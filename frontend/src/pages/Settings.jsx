import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, Loader2, ArrowLeft, Key, Cpu, Github, CheckCircle } from 'lucide-react';
import { api } from '../services/api';

const Settings = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  // Form states
  const [provider, setProvider] = useState('OpenAI');
  const [githubToken, setGithubToken] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const data = await api.getSettings();
        setProvider(data.embedding_provider || 'OpenAI');
        setGithubToken(data.github_token || '');
        setGeminiKey(data.gemini_api_key || '');
        setOpenaiKey(data.openai_api_key || '');
      } catch (err) {
        console.error('Failed to load settings', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);
    try {
      await api.updateSettings({
        embedding_provider: provider,
        github_token: githubToken || null,
        gemini_api_key: geminiKey || null,
        openai_api_key: openaiKey || null
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save settings', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-background text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-3 text-primary" />
        Loading configuration settings...
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-background p-8 text-gray-200">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate(-1)}
              className="p-2.5 bg-surface border border-border rounded-xl text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white leading-tight">Configuration Settings</h1>
              <p className="text-gray-400 text-xs mt-1">Configure model providers, API keys, and environment options.</p>
            </div>
          </div>
        </div>

        {/* Settings Form */}
        <form onSubmit={handleSave} className="bg-surface border border-border rounded-xl p-6 space-y-6 shadow-xl">
          {/* Embedding Provider */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-white">
              <Cpu className="w-4 h-4 text-primary" />
              Embedding Provider
            </label>
            <p className="text-xs text-gray-400">Choose the active model provider for vector embeddings and code retrieval.</p>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-primary"
            >
              <option value="OpenAI">OpenAI (text-embedding-3-small)</option>
              <option value="Gemini">Google Gemini (text-embedding-004)</option>
            </select>
          </div>

          {/* OpenAI Key */}
          {provider === 'OpenAI' && (
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-white">
                <Key className="w-4 h-4 text-primary" />
                OpenAI API Key
              </label>
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-primary font-mono"
              />
            </div>
          )}

          {/* Gemini Key */}
          {provider === 'Gemini' && (
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-white">
                <Key className="w-4 h-4 text-primary" />
                Gemini API Key
              </label>
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-primary font-mono"
              />
            </div>
          )}

          {/* GitHub Token */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-white">
              <Github className="w-4 h-4 text-primary" />
              GitHub Personal Access Token (PAT)
            </label>
            <p className="text-xs text-gray-400">Required to authorize imports for private repositories or bypass rate-limits.</p>
            <input
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_..."
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-primary font-mono"
            />
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <div className="flex items-center gap-2">
              {success && (
                <div className="flex items-center gap-2 text-green-400 text-xs font-semibold animate-fade-in">
                  <CheckCircle className="w-4 h-4" />
                  Settings saved successfully!
                </div>
              )}
            </div>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-black font-semibold text-sm px-5 py-2.5 rounded-lg transition-all shadow-lg active:scale-95 disabled:opacity-50"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;
