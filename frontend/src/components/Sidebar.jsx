import { Link } from 'react-router-dom';

const Sidebar = () => {
  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col min-h-screen">
      <div className="p-4 font-bold text-xl border-b border-gray-700">CodeAtlas</div>
      <nav className="flex-1 p-4 space-y-2">
        <Link to="/dashboard" className="block py-2 px-4 rounded hover:bg-gray-700">Dashboard</Link>
        <Link to="/repository/1" className="block py-2 px-4 rounded hover:bg-gray-700">Repository</Link>
        <Link to="/graph" className="block py-2 px-4 rounded hover:bg-gray-700">Graph Explorer</Link>
        <Link to="/analysis" className="block py-2 px-4 rounded hover:bg-gray-700">Analysis</Link>
        <Link to="/settings" className="block py-2 px-4 rounded hover:bg-gray-700">Settings</Link>
      </nav>
    </div>
  );
};

export default Sidebar;
