import { Link } from 'react-router-dom';

const Landing = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 text-gray-900">
      <h1 className="text-5xl font-bold mb-6">Welcome to CodeAtlas</h1>
      <p className="text-xl mb-8">AI Repository Intelligence Platform</p>
      <Link to="/dashboard" className="px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700">
        Go to Dashboard
      </Link>
    </div>
  );
};

export default Landing;
