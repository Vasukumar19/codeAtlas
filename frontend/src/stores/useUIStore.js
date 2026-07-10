import { create } from 'zustand'

export const useUIStore = create((set) => ({
  activeTab: 'graph', // graph, code, dashboard, execution, impact
  rightPanelMode: 'inspector', // inspector, ai
  
  setActiveTab: (tab) => set({ activeTab: tab }),
  setRightPanelMode: (mode) => set({ rightPanelMode: mode }),
}))
