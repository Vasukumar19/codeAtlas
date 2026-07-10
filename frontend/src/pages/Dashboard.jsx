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
