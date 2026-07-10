import useStore from '../store';

const TopNavigation = () => {
  const toggleTheme = useStore((state) => state.toggleTheme);
  
  return (
    <header className="bg-white shadow h-16 flex items-center justify-between px-6">
      <div className="font-semibold text-gray-800">Workspace</div>
      <button 
        onClick={toggleTheme}
        className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200"
      >
        Toggle Theme
      </button>
    </header>
  );
};

export default TopNavigation;
