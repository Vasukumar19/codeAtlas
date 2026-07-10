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
