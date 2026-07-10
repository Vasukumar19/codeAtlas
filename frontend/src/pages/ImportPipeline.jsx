import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Loader2, Database, BrainCircuit, Network, CheckCircle2 } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { api } from '../services/api'

export function ImportPipeline() {
  const navigate = useNavigate()
  const location = useLocation()
  const searchParams = new URLSearchParams(location.search)
  const repoId = searchParams.get('repoId')
  
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    if (!repoId) return;

    const poll = async () => {
      try {
        const res = await api.getRepositoryStatus(repoId);
        const status = res.status;
        
        if (status === 'NEW' || status === 'CLONING') {
          setCurrentStepIndex(0);
        } else if (status === 'READY_TO_PARSE') {
          setCurrentStepIndex(1);
        } else if (status === 'PARSING') {
          setCurrentStepIndex(2);
        } else if (status === 'PARSED') {
          setCurrentStepIndex(4); // All done
          setTimeout(() => {
            navigate(`/repo/${repoId}`);
          }, 1000);
          return; // Stop polling
        }
      } catch (e) {
        console.error(e);
      }
      setTimeout(poll, 2000);
    };
    
    poll();
  }, [repoId, navigate]);

  const steps = [
    { name: 'Cloning Repository', status: currentStepIndex > 0 ? 'done' : (currentStepIndex === 0 ? 'active' : 'pending'), icon: Database },
    { name: 'Parsing AST', status: currentStepIndex > 1 ? 'done' : (currentStepIndex === 1 ? 'active' : 'pending'), icon: Network },
    { name: 'Building Knowledge Graph', status: currentStepIndex > 2 ? 'done' : (currentStepIndex === 2 ? 'active' : 'pending'), icon: BrainCircuit },
    { name: 'Generating Embeddings', status: currentStepIndex > 3 ? 'done' : (currentStepIndex === 3 ? 'active' : 'pending'), icon: Database },
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
            onClick={() => navigate(repoId ? `/repo/${repoId}` : '/')}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            Skip to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
