import { create } from 'zustand'

export const useRepositoryStore = create((set) => ({
  activeRepositoryId: 'demo-repo',
  activeVersionId: 'v1.0',
  pinnedFiles: [],
  pinnedSymbols: [],
  
  setActiveRepository: (id) => set({ activeRepositoryId: id }),
  pinFile: (file) => set((state) => ({ 
    pinnedFiles: state.pinnedFiles.includes(file) ? state.pinnedFiles : [...state.pinnedFiles, file] 
  })),
  unpinFile: (file) => set((state) => ({ 
    pinnedFiles: state.pinnedFiles.filter(f => f !== file) 
  })),
}))
