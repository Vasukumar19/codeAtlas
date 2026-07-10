import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import { Play, Pause, StepForward, RotateCcw, Loader2 } from 'lucide-react';
import { api } from '@/services/api';
import useStore from '@/store';
import { useParams } from 'react-router-dom';

export function ExecutionFlow() {
  const { id } = useParams();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(true);
  const setActiveEntity = useStore(state => state.setActiveEntity);

  useEffect(() => {
    if (!id) return;

    const loadGraph = async () => {
      setLoading(true);
      try {
        const data = await api.getGraph(id);
        
        const cols = Math.ceil(Math.sqrt(data.nodes.length || 1));
        const spacing = 200;
        
        const formattedNodes = data.nodes.map((n, i) => ({
          id: n.id,
          data: { label: n.label, ...n.data },
          position: { 
            x: (i % cols) * spacing, 
            y: Math.floor(i / cols) * spacing 
          },
          style: {
            background: n.type === 'file' ? '#1e1e1e' : '#262626',
            color: '#fff',
            border: n.type === 'file' ? '1px solid #3b82f6' : '1px solid #a855f7',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '12px',
            width: 150,
            textAlign: 'center'
          }
        }));

        const formattedEdges = data.edges.map(e => ({
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.label,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#9ca3af',
          },
          style: { stroke: '#3b82f6' },
          animated: playing
        }));

        setNodes(formattedNodes);
        setEdges(formattedEdges);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadGraph();
  }, [id, setNodes, setEdges]); // Removed playing from dep array to avoid reloading

  useEffect(() => {
    setEdges(eds => eds.map(e => ({ ...e, animated: playing })));
  }, [playing, setEdges]);

  const onNodeClick = useCallback((event, node) => {
    setActiveEntity({ 
      id: node.id, 
      name: node.data.label, 
      type: node.style?.border?.includes('3b82f6') ? 'file' : 'symbol' 
    });
  }, [setActiveEntity]);

  if (loading) {
    return <div className="h-full flex items-center justify-center bg-[#0a0a0a]"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="h-full w-full relative bg-[#0a0a0a]">
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-surface border border-border rounded-full px-4 py-2 flex items-center gap-4 shadow-xl">
        <button className="text-gray-400 hover:text-white" onClick={() => setPlaying(false)}><RotateCcw className="w-5 h-5" /></button>
        <button 
          className="w-10 h-10 bg-primary hover:bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg"
          onClick={() => setPlaying(!playing)}
        >
          {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
        </button>
        <button className="text-gray-400 hover:text-white"><StepForward className="w-5 h-5" /></button>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        theme="dark"
      >
        <Controls className="bg-surface border-border fill-gray-400" />
        <MiniMap nodeColor="#262626" maskColor="rgba(0,0,0,0.7)" style={{ backgroundColor: '#171717' }} />
        <Background color="#262626" gap={16} />
      </ReactFlow>
    </div>
  );
}
