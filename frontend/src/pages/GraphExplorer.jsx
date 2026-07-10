import React, { useEffect, useState, useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../services/api';
import useStore from '../store';
import { useParams } from 'react-router-dom';
import { Loader2, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const GraphExplorer = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const setActiveEntity = useStore(state => state.setActiveEntity);
  const fgRef = useRef();

  useEffect(() => {
    if (!id) return;

    const loadGraph = async () => {
      setLoading(true);
      try {
        const data = await api.getGraph(id);
        
        const nodes = data.nodes.map(n => ({
          id: n.id,
          name: n.label || n.data?.label || n.id,
          type: n.type,
          val: n.type === 'directory' ? 10 : (n.type === 'file' ? 5 : 2),
          color: n.type === 'directory' ? '#f59e0b' : (n.type === 'file' ? '#3b82f6' : '#a855f7')
        }));

        const links = data.edges.map(e => ({
          source: e.source,
          target: e.target,
          label: e.label,
          color: 'rgba(255,255,255,0.1)'
        }));

        setGraphData({ nodes, links });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadGraph();
  }, [id]);

  const handleNodeClick = (node) => {
    // Zoom in on node
    fgRef.current.centerAt(node.x, node.y, 1000);
    fgRef.current.zoom(4, 1000);
    setActiveEntity({ id: node.id, name: node.name, type: node.type });
  };

  if (loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-gray-400 font-medium">Generating Physics Engine...</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-[#0a0a0a] overflow-hidden">
      <div className="absolute top-4 left-4 z-10 flex gap-2">
        <button 
          onClick={() => navigate(`/repo/${id}`)}
          className="p-3 bg-surface/80 backdrop-blur border border-white/10 rounded-xl text-gray-300 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="px-5 py-3 bg-surface/80 backdrop-blur border border-white/10 rounded-xl shadow-lg">
          <h2 className="text-white font-bold text-sm tracking-widest uppercase">Knowledge Graph</h2>
          <p className="text-gray-400 text-xs mt-1">Scroll to zoom. Drag to pan. Click nodes.</p>
        </div>
      </div>
      
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel="name"
        nodeColor="color"
        nodeRelSize={4}
        linkColor="color"
        linkWidth={1}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        onNodeClick={handleNodeClick}
        backgroundColor="#0a0a0a"
        d3VelocityDecay={0.3} // makes it stabilize faster
        cooldownTicks={100} // stop simulating after 100 ticks to save CPU
      />
    </div>
  );
};

export default GraphExplorer;
