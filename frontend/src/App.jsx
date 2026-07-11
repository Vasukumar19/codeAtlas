import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Landing from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import Repository from './pages/Repository';
import GraphExplorer from './pages/GraphExplorer';
import Analysis from './pages/Analysis';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/repository/:id" element={<Repository />} />
        <Route path="/repo/:id/flow" element={<GraphExplorer />} />
        <Route path="/repo/:id/analysis" element={<Analysis />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
