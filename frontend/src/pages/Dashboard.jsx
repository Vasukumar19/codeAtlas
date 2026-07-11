import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Activity, ShieldAlert, Zap, BookOpen, Layers, Loader2, Sparkles, ChevronRight, Code2, Route, FileWarning } from 'lucide-react'
import { motion } from 'framer-motion'
import { api } from '../services/api'
import useStore from '../store'

export function Dashboard() {
  const navigate = useNavigate()
  const { id } = useParams()
  const [repo, setRepo] = useState(null)
  const [stats, setStats] = useState(null)
  const [hotFiles, setHotFiles] = useState([])
  const { toggleChat } = useStore()
  
  useEffect(() => {
    const loadRepo = async () => {
      try {
        const repos = await api.getRepositories();
        if (repos.length > 0) {
          const targetRepo = repos.find(r => r.id === id) || repos[repos.length - 1]; 
          setRepo(targetRepo);
          const statsRes = await api.fetchRepositoryStats(targetRepo.id);
          setStats(statsRes);
          const hot = await api.getHotFiles(targetRepo.id);
          setHotFiles(hot);
        }
      } catch (e) {
        console.error(e);
      }
    };
    loadRepo();
  }, [id]);

  if (!repo) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-gray-400 font-medium">Analyzing Repository Intelligence...</p>
      </div>
    )
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 15 } }
  }

  return (
    <div className="relative p-8 h-full overflow-y-auto overflow-x-hidden">
      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none -translate-x-1/2 -translate-y-1/2" />
      <div className="absolute top-1/2 right-0 w-[400px] h-[400px] bg-accent/10 rounded-full blur-[100px] pointer-events-none translate-x-1/3 -translate-y-1/2" />

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 max-w-7xl mx-auto"
      >
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
          <motion.div variants={itemVariants}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                <Code2 className="w-6 h-6 text-primary" />
              </div>
              <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                Repository Intelligence
              </h1>
            </div>
            <p className="text-gray-400 text-lg flex items-center gap-2">
              <span>{repo.owner}</span>
              <span className="text-gray-600">/</span>
              <span className="text-gray-300 font-semibold">{repo.name}</span>
            </p>
          </motion.div>

          <motion.button 
            variants={itemVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleChat}
            className="group px-6 py-3 bg-gradient-to-r from-accent to-primary hover:from-purple-500 hover:to-blue-500 text-white rounded-xl font-semibold shadow-[0_0_40px_rgba(139,92,246,0.3)] transition-all flex items-center gap-3"
          >
            <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
            <span>Ask CodeAtlas AI</span>
          </motion.button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <Widget variants={itemVariants} title="Repository Score" value={stats?.score || "..."} icon={Activity} color="text-green-400" />
          <Widget variants={itemVariants} title="Technical Debt" value={stats?.technicalDebt || "..."} icon={ShieldAlert} color="text-blue-400" />
          <Widget variants={itemVariants} title="Knowledge Coverage" value={stats?.knowledgeCoverage || "..."} icon={BookOpen} color="text-purple-400" />
          <Widget variants={itemVariants} title="Graph Density" value={stats?.graphDensity || "..."} icon={Layers} color="text-orange-400" />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <motion.div 
            variants={itemVariants}
            whileHover={{ scale: 1.01 }}
            className="lg:col-span-2 bg-surface/50 backdrop-blur-xl border border-white/5 rounded-2xl p-8 h-[400px] flex items-center justify-center relative overflow-hidden group cursor-pointer shadow-2xl" 
            onClick={() => navigate(`/repo/${repo.id}/flow`)}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03] pointer-events-none" />
            
            <div className="text-center relative z-10">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary to-accent rounded-2xl p-[1px] mb-6 shadow-lg shadow-primary/20 group-hover:shadow-primary/40 transition-shadow">
                <div className="w-full h-full bg-surface rounded-2xl flex items-center justify-center">
                  <Layers className="w-10 h-10 text-white" />
                </div>
              </div>
              <h3 className="text-3xl font-bold text-white mb-3 tracking-tight">Explore the Knowledge Graph</h3>
              <p className="text-gray-400 text-lg mb-6 max-w-md mx-auto">Dive into the deep structural execution flow of your codebase using our physics-based explorer.</p>
              
              <div className="inline-flex items-center gap-2 text-primary font-medium group-hover:gap-4 transition-all">
                Enter Graph View <ChevronRight className="w-5 h-5" />
              </div>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="bg-surface/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 shadow-2xl flex flex-col">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h3 className="text-xl font-bold text-white">Hot Files</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
              <ul className="space-y-4">
                {hotFiles.map((file, i) => (
                  <motion.li 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    key={i} 
                    className="flex flex-col gap-2 p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-colors cursor-default"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-gray-200 font-mono text-sm truncate mr-2" title={file.name}>
                        {file.name.split('/').pop()}
                      </span>
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                        file.risk === 'High Risk' ? 'text-orange-400 bg-orange-400/10 border border-orange-400/20' :
                        file.risk === 'Med Risk' ? 'text-yellow-400 bg-yellow-400/10 border border-yellow-400/20' :
                        'text-green-400 bg-green-400/10 border border-green-400/20'
                      }`}>
                        {file.risk}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 font-mono truncate" title={file.name}>
                      {file.name}
                    </div>
                  </motion.li>
                ))}
                {hotFiles.length === 0 && (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-gray-500 text-sm">No hot files found yet.</p>
                  </div>
                )}
              </ul>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <ActionCard
            variants={itemVariants}
            title="Execution Flow"
            description="Trace route and function calls using resolved CALLS edges."
            icon={Route}
            onClick={() => navigate(`/repo/${repo.id}/flow`)}
          />
          <ActionCard
            variants={itemVariants}
            title="Impact & Security"
            description="Inspect blast radius and concrete static findings."
            icon={FileWarning}
            onClick={() => navigate(`/repo/${repo.id}/analysis`)}
          />
          <ActionCard
            variants={itemVariants}
            title="Documentation Draft"
            description="Generate a module README from parsed structure and enrichment."
            icon={BookOpen}
            onClick={() => navigate(`/repo/${repo.id}/analysis`)}
          />
        </div>
      </motion.div>
    </div>
  )
}

function ActionCard({ title, description, icon: Icon, onClick, variants }) {
  return (
    <motion.button
      variants={variants}
      whileHover={{ y: -3 }}
      onClick={onClick}
      className="text-left bg-surface/50 border border-white/5 rounded-lg p-5 hover:border-primary/40 hover:bg-white/[0.04] transition-colors"
    >
      <Icon className="w-5 h-5 text-primary mb-4" />
      <div className="font-bold text-white mb-2">{title}</div>
      <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </motion.button>
  )
}

function Widget({ title, value, icon: Icon, color, variants }) {
  return (
    <motion.div 
      variants={variants}
      whileHover={{ y: -5 }}
      className="bg-surface/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 relative overflow-hidden group shadow-lg"
    >
      <div className={`absolute top-0 right-0 w-32 h-32 bg-white opacity-[0.02] rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 group-hover:opacity-10 transition-opacity ${color.replace('text', 'bg')}`} />
      
      <div className="flex items-start justify-between relative z-10">
        <div>
          <div className="text-sm text-gray-400 font-medium mb-2">{title}</div>
          <div className="text-4xl font-black text-white tracking-tight">{value}</div>
        </div>
        <div className={`p-3 rounded-xl bg-white/5 border border-white/5 shadow-inner ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )
}
