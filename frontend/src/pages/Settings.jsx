import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, Loader2, ArrowLeft, Key, Cpu, Github, CheckCircle, ShieldAlert, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

const Settings = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [unauthorized, setUnauthorized] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Authentication token
  const [adminToken, setAdminToken] = useState(localStorage.getItem('codeatlas_admin_token') || '');

  // Form states
  const [provider, setProvider] = useState('OpenAI');
  const [githubToken, setGithubToken] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');

  const fetchSettings = async () => {
    setLoading(true);
    setUnauthorized(false);
    setErrorMessage('');
    try {
      const data = await api.getSettings();
      setProvider(data.embedding_provider || 'OpenAI');
      setGithubToken(data.github_token || '');
      setGeminiKey(data.gemini_api_key || '');
      setOpenaiKey(data.openai_api_key || '');
    } catch (err) {
      console.error('Failed to load settings', err);
      // Check if it is a 401 Unauthorized
      if (err.message && err.message.includes('401')) {
        setUnauthorized(true);
      } else {
        setErrorMessage('Failed to connect to the settings service.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleAdminTokenChange = (e) => {
    const val = e.target.value;
    setAdminToken(val);
    localStorage.setItem('codeatlas_admin_token', val);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);
    setErrorMessage('');
    try {
      await api.updateSettings({
        embedding_provider: provider,
        github_token: githubToken || null,
        gemini_api_key: geminiKey || null,
        openai_api_key: openaiKey || null
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      // Reload values after saving to refresh masks
      await fetchSettings();
    } catch (err) {
      console.error('Failed to save settings', err);
      setErrorMessage(err.message || 'Failed to update settings configuration.');
    } finally {
      setSaving(false);
    }
  };

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
              <p className="text-gray-400 text-xs mt-1">Configure model providers, API keys, and environment options securely.</p>
            </div>
          </div>
        </div>

        {/* Admin Authorization Block */}
        <div className="bg-surface border border-border rounded-xl p-5 space-y-3 shadow-lg">
          <label className="flex items-center gap-2 text-sm font-semibold text-white">
            <ShieldAlert className="w-4 h-4 text-accent" />
            Admin Access Authorization
          </label>
          <p className="text-xs text-gray-400">If the backend server enforces <code>ADMIN_API_TOKEN</code>, enter your authorization token here to unlock settings access.</p>
          <div className="flex gap-2">
            <input
              type="password"
              value={adminToken}
              onChange={handleAdminTokenChange}
              placeholder="Enter authorization token..."
              className="flex-1 bg-background border border-border rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-accent font-mono"
            />
            <button
              type="button"
              onClick={fetchSettings}
              className="px-4 py-2 bg-background border border-border hover:bg-white/5 text-xs font-semibold rounded-lg transition-colors"
            >
              Apply Token
            </button>
          </div>
        </div>

        {loading ? (
          <div className="bg-surface border border-border rounded-xl p-8 flex items-center justify-center text-gray-400">
            <Loader2 className="w-5 h-5 animate-spin mr-3 text-primary" />
            Retrieving configurations...
          </div>
        ) : unauthorized ? (
          <div className="bg-surface border border-red-500/30 rounded-xl p-8 text-center space-y-4">
            <AlertTriangle className="w-10 h-10 text-red-400 mx-auto animate-bounce" />
            <h3 className="text-lg font-bold text-white">Unauthorized Settings Access</h3>
            <p className="text-sm text-gray-400 max-w-md mx-auto">Access denied by settings API. Please enter a valid token in the Admin Access Authorization input above to unlock this panel.</p>
          </div>
        ) : (
          /* Settings Form */
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
                  onFocus={(e) => { if (e.target.value === '••••••••') setOpenaiKey(''); }}
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
                  onFocus={(e) => { if (e.target.value === '••••••••') setGeminiKey(''); }}
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
                onFocus={(e) => { if (e.target.value === '••••••••') setGithubToken(''); }}
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
                {errorMessage && (
                  <div className="text-red-400 text-xs font-semibold">
                    {errorMessage}
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
        )}
      </div>
    </div>
  );
};

export default Settings;
