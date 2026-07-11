import React, { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { AlertTriangle, BookOpen, Loader2, Network, ShieldAlert } from 'lucide-react'
import { api } from '../services/api'

const Analysis = () => {
  const { id } = useParams()
  const [graph, setGraph] = useState(null)
  const [security, setSecurity] = useState([])
  const [docs, setDocs] = useState(null)
  const [impact, setImpact] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    const load = async () => {
      setLoading(true)
      try {
        const [graphData, findings, docsDraft] = await Promise.all([
          api.getGraph(id),
          api.getSecurityFindings(id),
          api.generateDocs(id),
        ])
        setGraph(graphData)
        setSecurity(findings)
        setDocs(docsDraft)
        const firstNode = graphData.nodes.find((node) => node.type === 'route' || node.type === 'symbol' || node.type === 'file')
        if (firstNode) {
          setImpact(await api.getImpactAnalysis(id, firstNode.id))
        }
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const graphSummary = useMemo(() => {
    if (!graph) return { nodes: 0, calls: 0, routes: 0 }
    return {
      nodes: graph.nodes.length,
      calls: graph.edges.filter((edge) => edge.label === 'CALLS').length,
      routes: graph.nodes.filter((node) => node.type === 'route').length,
    }
  }, [graph])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-background text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-3 text-primary" />
        Loading repository analysis...
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-background p-6 text-gray-200">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Repository Analysis</h1>
          <p className="text-gray-400">Graph traversal, security findings, and generated documentation are backed by the current imported repository data.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard icon={Network} label="Graph Nodes" value={graphSummary.nodes} />
          <MetricCard icon={Network} label="CALLS Edges" value={graphSummary.calls} />
          <MetricCard icon={ShieldAlert} label="Findings" value={security.length} />
        </div>

        <section className="bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Network className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-white">Impact Analysis</h2>
          </div>
          {impact ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Entities Reached</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.total_entities}</div>
              </div>
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Files</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.files}</div>
              </div>
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Routes</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.routes}</div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No graph entity is available for impact traversal yet.</p>
          )}
        </section>

        <section className="bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <h2 className="font-bold text-white">Security Findings</h2>
          </div>
          <div className="space-y-3">
            {security.map((finding, index) => (
              <div key={`${finding.path}-${finding.line}-${index}`} className="bg-background border border-border rounded-lg p-4">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <span className="font-semibold text-white">{finding.message}</span>
                  <span className="text-xs uppercase text-yellow-300 bg-yellow-300/10 border border-yellow-300/20 rounded px-2 py-1">{finding.severity}</span>
                </div>
                <div className="text-xs text-gray-500 font-mono mb-2">{finding.path}:{finding.line}</div>
                <code className="block text-xs text-gray-300 bg-black/30 rounded p-2 overflow-x-auto">{finding.snippet}</code>
              </div>
            ))}
            {security.length === 0 && <p className="text-gray-500 text-sm">No static security findings detected.</p>}
          </div>
        </section>

        <section className="bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-white">Documentation Draft</h2>
          </div>
          <pre className="bg-background border border-border rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap overflow-x-auto">{docs?.markdown || 'No documentation draft available.'}</pre>
        </section>
      </div>
    </div>
  )
}

function MetricCard({ icon: Icon, label, value }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-5">
      <Icon className="w-5 h-5 text-primary mb-4" />
      <div className="text-gray-500 uppercase text-xs mb-1">{label}</div>
      <div className="text-3xl font-bold text-white">{value}</div>
    </div>
  )
}

export default Analysis
