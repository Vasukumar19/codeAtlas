import { Outlet, useParams } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNavigation from './TopNavigation';
import { CodeViewer } from '../components/CodeViewer';
import useStore from '../store';
import { X } from 'lucide-react';

const Layout = () => {
  const viewingFile = useStore(state => state.viewingFile);
  const setViewingFile = useStore(state => state.setViewingFile);
  const { id } = useParams();

  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden relative">
      <Sidebar />
      <div className="flex flex-col flex-1 relative">
        <TopNavigation />
        <main className="flex-1 overflow-auto p-6 relative">
          <Outlet />
          
          {viewingFile && id && (
            <div className="absolute inset-4 z-50 bg-[#1e1e1e] border border-border shadow-2xl rounded-xl flex flex-col overflow-hidden">
              <div className="bg-surface px-4 py-2 flex items-center justify-between border-b border-border">
                <span className="text-gray-300 text-sm font-mono">{viewingFile.name}</span>
                <button onClick={() => setViewingFile(null)} className="text-gray-500 hover:text-white transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-hidden relative">
                 <CodeViewer repositoryId={id} fileId={viewingFile.id} />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Layout;
