import { create } from 'zustand';

const useStore = create((set) => ({
  user: null,
  theme: 'dark',
  activeEntity: null,
  viewingFile: null,
  isChatOpen: false,
  setActiveEntity: (entity) => set({ activeEntity: entity }),
  setViewingFile: (file) => set({ viewingFile: file }),
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
}));

export default useStore;
