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
