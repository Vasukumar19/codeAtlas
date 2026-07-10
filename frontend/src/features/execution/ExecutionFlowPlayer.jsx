import React, { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import { Play, Pause, StepForward, RotateCcw } from 'lucide-react';

const initialNodes = [
  { id: '1', position: { x: 250, y: 50 }, data: { label: 'POST /login (Route)' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px' } },
  { id: '2', position: { x: 250, y: 150 }, data: { label: 'AuthController' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
  { id: '3', position: { x: 250, y: 250 }, data: { label: 'AuthService' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
  { id: '4', position: { x: 250, y: 350 }, data: { label: 'UserRepository' }, style: { background: '#1e1e1e', color: '#fff', border: '1px solid #262626', borderRadius: '8px' } },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#3b82f6' } },
];

export function ExecutionFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-full w-full relative bg-[#0a0a0a]">
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-surface border border-border rounded-full px-4 py-2 flex items-center gap-4 shadow-xl">
        <button className="text-gray-400 hover:text-white"><RotateCcw className="w-5 h-5" /></button>
        <button className="w-10 h-10 bg-primary hover:bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg"><Play className="w-5 h-5 ml-1" /></button>
        <button className="text-gray-400 hover:text-white"><StepForward className="w-5 h-5" /></button>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
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
