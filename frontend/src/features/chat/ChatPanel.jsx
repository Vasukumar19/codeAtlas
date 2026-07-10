import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Bot, User, Loader2, Code2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import useStore from '../../store';
import { api } from '../../services/api';
import { useParams } from 'react-router-dom';

export function ChatPanel() {
  const { isChatOpen, toggleChat } = useStore();
  const { id: paramId } = useParams();
  const [repoId, setRepoId] = useState(paramId);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your CodeAtlas AI Assistant. Ask me anything about this repository. For example:\n- "Can you explain the execution flow of the main router?"\n- "Are there any security risks?"' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isChatOpen]);

  useEffect(() => {
    if (!paramId && isChatOpen) {
      api.getRepositories().then(repos => {
        if (repos.length > 0) {
          setRepoId(repos[repos.length - 1].id);
        }
      }).catch(console.error);
    } else if (paramId) {
      setRepoId(paramId);
    }
  }, [paramId, isChatOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !repoId) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // The API returns the ContextPackage which has an "analysis" or "summary"
      // Our backend endpoint is /api/v1/intelligence/ask
      const response = await api.askAI(userMessage, repoId);
      
      const content = response.analysis?.text || response.summary || "I processed your request, but couldn't generate a text response.";
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: content,
        context: response // Keep context if we want to build UI for it later
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error while processing your request. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isChatOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleChat}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100]"
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '100%', opacity: 0.5 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0.5 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 w-[500px] h-screen max-w-[90vw] bg-surface/95 backdrop-blur-2xl border-l border-white/10 z-[110] flex flex-col shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/20 rounded-lg">
                  <Bot className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-white font-bold text-lg leading-tight">CodeAtlas AI</h3>
                  <p className="text-gray-400 text-xs font-medium tracking-wide uppercase">Repository Assistant</p>
                </div>
              </div>
              <button 
                onClick={toggleChat}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar scroll-smooth">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-1 ${
                    msg.role === 'user' ? 'bg-accent/20 text-accent' : 'bg-primary/20 text-primary'
                  }`}>
                    {msg.role === 'user' ? <User className="w-4 h-4" /> : <Code2 className="w-4 h-4" />}
                  </div>
                  
                  <div className={`max-w-[80%] rounded-2xl p-4 ${
                    msg.role === 'user' 
                      ? 'bg-accent/10 border border-accent/20 text-white rounded-tr-sm' 
                      : 'bg-white/5 border border-white/10 text-gray-200 rounded-tl-sm'
                  }`}>
                    {msg.role === 'user' ? (
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none 
                        prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 
                        prose-a:text-primary hover:prose-a:text-blue-400">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm p-4 flex items-center gap-3">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="text-sm text-gray-400 font-medium tracking-wide animate-pulse">Analyzing repository semantics...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/5 bg-black/20">
              <form onSubmit={handleSubmit} className="relative flex items-end">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                  placeholder="Ask a question about this repository..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl pl-4 pr-12 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none max-h-32 min-h-[52px] custom-scrollbar"
                  rows="1"
                  style={{ height: "auto" }}
                />
                <button 
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="absolute right-2 bottom-2 p-1.5 bg-primary text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
              <div className="text-center mt-3">
                <span className="text-[10px] text-gray-500 font-medium tracking-widest uppercase">Powered by CodeAtlas Hybrid Retrieval Engine</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
