import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { api } from '../services/api';

export function CodeViewer({ repositoryId, fileId }) {
  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!repositoryId || !fileId) return;

    const fetchContent = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getFileContent(repositoryId, fileId);
        setContent(data.content);
        // Basic mapping, Monaco expects standard names like 'python', 'javascript'
        setLanguage(data.language.toLowerCase());
      } catch (err) {
        console.error(err);
        setError('Failed to load file content.');
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [repositoryId, fileId]);

  if (loading) {
    return <div className="h-full flex items-center justify-center text-gray-500">Loading code...</div>;
  }

  if (error) {
    return <div className="h-full flex items-center justify-center text-red-500">{error}</div>;
  }

  if (!content) {
    return <div className="h-full flex items-center justify-center text-gray-500">Select a file to view its source code.</div>;
  }

  return (
    <div className="h-full w-full border border-border rounded-lg overflow-hidden bg-[#1e1e1e]">
      <Editor
        height="100%"
        language={language}
        theme="vs-dark"
        value={content}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
        }}
      />
    </div>
  );
}
