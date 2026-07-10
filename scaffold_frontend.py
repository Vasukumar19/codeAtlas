import os

files = {
    "frontend/vite.config.js": """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
""",
    "frontend/tailwind.config.js": """
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        surface: '#171717',
        primary: '#3b82f6',
        accent: '#8b5cf6',
        border: '#262626'
      }
    },
  },
  plugins: [],
}
""",
    "frontend/postcss.config.js": """
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
    "frontend/index.html": """
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CodeAtlas</title>
  </head>
  <body class="bg-background text-gray-100 antialiased overflow-hidden">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
    "frontend/src/index.css": """
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body, #root {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}
""",
    "frontend/src/main.jsx": """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app/App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
    "frontend/src/app/App.jsx": """
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/layouts/Layout'
import { Landing } from '@/pages/Landing'
import { Dashboard } from '@/pages/Dashboard'
import { ImportPipeline } from '@/pages/ImportPipeline'
import { ExecutionFlow } from '@/features/execution/ExecutionFlowPlayer'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/import" element={<ImportPipeline />} />
          <Route element={<Layout />}>
            <Route path="/repo/:id" element={<Dashboard />} />
            <Route path="/repo/:id/flow" element={<ExecutionFlow />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
""",
    "frontend/src/layouts/Layout.jsx": """
import { Outlet } from 'react-router-dom'
import { LeftSidebar } from './LeftSidebar'
import { RightInspector } from './RightInspector'

export function Layout() {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <LeftSidebar />
      <main className="flex-1 relative border-l border-r border-border">
        <Outlet />
      </main>
      <RightInspector />
    </div>
  )
}
""",
    "frontend/src/layouts/LeftSidebar.jsx": """
import { FolderGit2, Search, Settings } from 'lucide-react'

export function LeftSidebar() {
  return (
    <div className="w-64 flex flex-col bg-surface border-r border-border h-full p-4">
      <div className="flex items-center gap-2 mb-8 text-primary">
        <FolderGit2 className="w-6 h-6" />
        <span className="font-bold text-xl tracking-tight text-white">CodeAtlas</span>
      </div>
      
      <div className="flex-1">
        <div className="relative mb-6">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
          <input 
            type="text" 
            placeholder="Search everything..." 
            className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-primary text-gray-200"
          />
        </div>
        
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Repository</div>
        <ul className="space-y-1">
          <li className="px-3 py-2 rounded-md bg-white/5 text-sm cursor-pointer hover:bg-white/10 transition-colors">Explorer</li>
          <li className="px-3 py-2 rounded-md text-gray-400 text-sm cursor-pointer hover:bg-white/5 transition-colors">Graph Filters</li>
          <li className="px-3 py-2 rounded-md text-gray-400 text-sm cursor-pointer hover:bg-white/5 transition-colors">Dependencies</li>
        </ul>
      </div>
      
      <div className="pt-4 border-t border-border mt-auto flex items-center gap-2 text-gray-400 hover:text-white cursor-pointer transition-colors">
        <Settings className="w-4 h-4" />
        <span className="text-sm">Settings</span>
      </div>
    </div>
  )
}
""",
    "frontend/src/layouts/RightInspector.jsx": """
import { Brain, FileCode, CheckCircle2 } from 'lucide-react'

export function RightInspector() {
  return (
    <div className="w-80 flex flex-col bg-surface border-l border-border h-full">
      <div className="p-4 border-b border-border flex items-center gap-2">
        <Brain className="w-5 h-5 text-accent" />
        <span className="font-semibold text-sm">Intelligence</span>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {/* Mock Structured AI Card */}
        <div className="bg-background rounded-lg border border-border overflow-hidden">
          <div className="bg-white/5 px-3 py-2 text-xs font-medium border-b border-border uppercase tracking-wider text-gray-400">
            Execution Flow
          </div>
          <div className="p-3 text-sm text-gray-300">
            Authentication starts from <span className="text-primary font-mono bg-primary/10 px-1 rounded">POST /login</span> and cascades to the user repository.
          </div>
        </div>

        <div className="bg-background rounded-lg border border-border overflow-hidden">
          <div className="bg-white/5 px-3 py-2 text-xs font-medium border-b border-border uppercase tracking-wider text-gray-400">
            Evidence
          </div>
          <div className="p-3 space-y-2">
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <FileCode className="w-3.5 h-3.5 text-gray-500" />
              <span className="truncate">auth/routes.py</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <FileCode className="w-3.5 h-3.5 text-gray-500" />
              <span className="truncate">auth/service.py</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-4 border-t border-border">
        <input 
          type="text" 
          placeholder="Ask Repository..." 
          className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-accent text-gray-200"
        />
      </div>
    </div>
  )
}
""",
    "frontend/src/pages/Landing.jsx": """
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Github } from 'lucide-react'

export function Landing() {
  const navigate = useNavigate()
  
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[100px]" />
      
      <div className="z-10 text-center max-w-3xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm text-gray-300 mb-8"
        >
          <span className="w-2 h-2 rounded-full bg-green-500" />
          CodeAtlas v1.0
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6"
        >
          Understand any GitHub Repository <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">instantly.</span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-xl text-gray-400 mb-12"
        >
          Paste a repository URL. Watch CodeAtlas build its Knowledge Graph, vectorize architecture, and prepare interactive intelligence.
        </motion.p>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center gap-4 w-full max-w-xl mx-auto"
        >
          <div className="relative flex-1 w-full">
            <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input 
              type="text" 
              placeholder="https://github.com/fastapi/fastapi" 
              className="w-full bg-surface border border-white/10 rounded-xl pl-12 pr-4 py-4 text-lg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-white shadow-2xl"
            />
          </div>
          <button 
            onClick={() => navigate('/import')}
            className="w-full sm:w-auto px-8 py-4 bg-primary hover:bg-blue-600 text-white rounded-xl font-semibold flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)]"
          >
            Import
            <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </div>
  )
}
""",
    "frontend/src/pages/ImportPipeline.jsx": """
import { motion } from 'framer-motion'
import { Loader2, Database, BrainCircuit, Network, CheckCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function ImportPipeline() {
  const navigate = useNavigate()
  
  const steps = [
    { name: 'Cloning Repository', status: 'done', icon: Database },
    { name: 'Parsing AST', status: 'done', icon: Network },
    { name: 'Building Knowledge Graph', status: 'active', icon: BrainCircuit },
    { name: 'Generating Embeddings', status: 'pending', icon: Database },
  ]
  
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-surface border border-border rounded-xl p-8 shadow-2xl">
        <h2 className="text-2xl font-bold text-white mb-8">Building Repository Intelligence Model</h2>
        
        <div className="space-y-6">
          {steps.map((step, i) => {
            const Icon = step.icon
            return (
              <div key={i} className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border ${
                  step.status === 'done' ? 'bg-green-500/10 border-green-500/30 text-green-500' :
                  step.status === 'active' ? 'bg-primary/10 border-primary/30 text-primary' :
                  'bg-white/5 border-white/10 text-gray-500'
                }`}>
                  {step.status === 'done' ? <CheckCircle2 className="w-5 h-5" /> : 
                   step.status === 'active' ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                   <Icon className="w-5 h-5" />}
                </div>
                <div>
                  <h3 className={`font-semibold ${step.status === 'pending' ? 'text-gray-500' : 'text-gray-200'}`}>
                    {step.name}
                  </h3>
                  {step.status === 'active' && (
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="h-1 bg-primary rounded-full mt-2 w-48"
                    />
                  )}
                </div>
              </div>
            )
          })}
        </div>
        
        <div className="mt-12 flex justify-end">
          <button 
            onClick={() => navigate('/repo/demo')}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            Skip to Dashboard (Demo)
          </button>
        </div>
      </div>
    </div>
  )
}
""",
    "frontend/src/pages/Dashboard.jsx": """
import { useNavigate } from 'react-router-dom'
import { Activity, ShieldAlert, Zap, BookOpen, Layers } from 'lucide-react'

export function Dashboard() {
  const navigate = useNavigate()
  
  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Repository Intelligence</h1>
          <p className="text-gray-400">FastAPI/FastAPI</p>
        </div>
        <button className="px-6 py-3 bg-gradient-to-r from-accent to-primary hover:from-purple-500 hover:to-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-primary/20 transition-all flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Explain This Repository
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Widget title="Repository Score" value="A+" icon={Activity} color="text-green-400" />
        <Widget title="Technical Debt" value="Low" icon={ShieldAlert} color="text-blue-400" />
        <Widget title="Knowledge Coverage" value="94%" icon={BookOpen} color="text-purple-400" />
        <Widget title="Graph Density" value="High" icon={Layers} color="text-orange-400" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6 h-96 flex items-center justify-center relative overflow-hidden group cursor-pointer" onClick={() => navigate('/repo/demo/flow')}>
          <div className="absolute inset-0 bg-primary/5 group-hover:bg-primary/10 transition-colors" />
          <div className="text-center">
            <Zap className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Execution Flow Player</h3>
            <p className="text-gray-400">Click to visualize the massive Graph Explorer</p>
          </div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Hot Files</h3>
          <ul className="space-y-3">
            <li className="flex items-center justify-between text-sm">
              <span className="text-gray-300 font-mono">auth/routes.py</span>
              <span className="text-orange-400 bg-orange-400/10 px-2 py-0.5 rounded text-xs">High Risk</span>
            </li>
            <li className="flex items-center justify-between text-sm">
              <span className="text-gray-300 font-mono">core/security.py</span>
              <span className="text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded text-xs">Med Risk</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function Widget({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 flex items-start justify-between">
      <div>
        <div className="text-sm text-gray-400 font-medium mb-1">{title}</div>
        <div className="text-3xl font-bold text-white">{value}</div>
      </div>
      <div className={`p-2 rounded-lg bg-white/5 ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
    </div>
  )
}
""",
    "frontend/src/features/execution/ExecutionFlowPlayer.jsx": """
import React, { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import { Play, Pause, StepForward, RotateCcw } from 'lucide-react';

const initialNodes = [
  { id: '1', position: { x: 250, y: 50 }, data: { label: 'POST /login (Route)' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px' } },
  { id: '2', position: { x: 250, y: 150 }, data: { label: 'AuthController' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
  { id: '3', position: { x: 250, y: 250 }, data: { label: 'AuthService' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
  { id: '4', position: { x: 250, y: 350 }, data: { label: 'UserRepository' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#3b82f6' } },
];

export function ExecutionFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-full w-full relative bg-[#0a0a0a]">
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-surface border border-border rounded-full px-4 py-2 flex items-center gap-4 shadow-xl">
        <button className="text-gray-400 hover:text-white"><RotateCcw className="w-5 h-5" /></button>
        <button className="w-10 h-10 bg-primary hover:bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg"><Play className="w-5 h-5 ml-1" /></button>
        <button className="text-gray-400 hover:text-white"><StepForward className="w-5 h-5" /></button>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        theme="dark"
      >
        <Controls className="bg-surface border-border fill-gray-400" />
        <MiniMap nodeColor="#262626" maskColor="rgba(0,0,0,0.7)" style={{ backgroundColor: '#171717' }} />
        <Background color="#262626" gap={16} />
      </ReactFlow>
    </div>
  );
}
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
