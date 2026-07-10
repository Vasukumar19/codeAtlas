import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-4xl font-bold mb-4">404 - Not Found</h2>
      <Link to="/" className="text-blue-500 hover:underline">Return Home</Link>
    </div>
  );
};

export default NotFound;
