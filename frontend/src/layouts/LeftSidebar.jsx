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
