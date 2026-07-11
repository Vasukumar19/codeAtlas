import React, { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AlertTriangle, BookOpen, Loader2, Network, ShieldAlert } from 'lucide-react'
import { api } from '../services/api'

const Analysis = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [graph, setGraph] = useState(null)
  const [security, setSecurity] = useState([])
  const [docs, setDocs] = useState(null)
  const [impact, setImpact] = useState(null)
  const [loading, setLoading] = useState(true)

  // Picker lists
  const [repositories, setRepositories] = useState([])
  const [selectedRepoId, setSelectedRepoId] = useState(id || '')
  const [selectedEntityId, setSelectedEntityId] = useState('')

  // Load repositories if no id is active in params
  useEffect(() => {
    if (!id) {
      setLoading(true)
      api.getRepositories().then(repos => {
        setRepositories(repos)
        setLoading(false)
      }).catch(err => {
        console.error(err)
        setLoading(false)
      })
    }
  }, [id])

  // Load analysis data when id changes
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
        
        // Default to first interactive node for initial impact rendering
        const firstNode = graphData.nodes?.find((node) => node.type === 'route' || node.type === 'symbol' || node.type === 'file')
        if (firstNode) {
          setSelectedEntityId(firstNode.id)
          setImpact(await api.getImpactAnalysis(id, firstNode.id))
        } else {
          setSelectedEntityId('')
          setImpact(null)
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
      nodes: graph.nodes?.length || 0,
      calls: graph.edges?.filter((edge) => edge.label === 'CALLS').length || 0,
      routes: graph.nodes?.filter((node) => node.type === 'route').length || 0,
    }
  }, [graph])

  const handleRepoChange = (repoId) => {
    setSelectedRepoId(repoId)
    if (repoId) {
      navigate(`/repo/${repoId}/analysis`)
    } else {
      navigate('/analysis')
    }
  }

  const handleEntityChange = async (entityId) => {
    setSelectedEntityId(entityId)
    if (entityId) {
      try {
        setImpact(await api.getImpactAnalysis(id, entityId))
      } catch (err) {
        console.error(err)
      }
    } else {
      setImpact(null)
    }
  }

  if (!id) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-background text-gray-200 p-6">
        <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8 shadow-2xl text-center">
          <Network className="w-12 h-12 text-primary mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold text-white mb-2">Select a Repository</h2>
          <p className="text-gray-400 text-sm mb-6">Choose a repository from the list below to view its advanced structural code graphs, security findings, and generated documentation.</p>
          <select
            value={selectedRepoId}
            onChange={(e) => handleRepoChange(e.target.value)}
            className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-primary mb-4"
          >
            <option value="">Choose a repository...</option>
            {repositories.map(repo => (
              <option key={repo.id} value={repo.id}>{repo.name}</option>
            ))}
          </select>
          {repositories.length === 0 && (
            <p className="text-xs text-gray-500">No repositories imported yet. Go to Dashboard to import one.</p>
          )}
        </div>
      </div>
    )
  }

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
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Repository Analysis</h1>
            <p className="text-gray-400 text-sm">Graph traversal, security findings, and generated documentation are backed by the current imported repository data.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 uppercase font-semibold">Active Repo:</span>
            <select
              value={id}
              onChange={(e) => handleRepoChange(e.target.value)}
              className="bg-surface border border-border rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-primary"
            >
              <option value="">Choose repo...</option>
              {repositories.map(repo => (
                <option key={repo.id} value={repo.id}>{repo.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard icon={Network} label="Graph Nodes" value={graphSummary.nodes} />
          <MetricCard icon={Network} label="CALLS Edges" value={graphSummary.calls} />
          <MetricCard icon={ShieldAlert} label="Findings" value={security.length} />
        </div>

        <section className="bg-surface border border-border rounded-lg p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Network className="w-5 h-5 text-primary" />
              <h2 className="font-bold text-white">Impact Analysis (Blast Radius)</h2>
            </div>
            {graph && graph.nodes && (
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Target Entity:</span>
                <select
                  value={selectedEntityId}
                  onChange={(e) => handleEntityChange(e.target.value)}
                  className="bg-background border border-border rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-primary max-w-xs font-mono"
                >
                  <option value="">Select entity...</option>
                  {graph.nodes
                    .filter(node => ['route', 'symbol', 'file'].includes(node.type))
                    .map(node => (
                      <option key={node.id} value={node.id}>
                        [{node.type.toUpperCase()}] {node.label || node.name || node.id}
                      </option>
                    ))}
                </select>
              </div>
            )}
          </div>
          
          {impact ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Entities Reached</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.total_entities}</div>
              </div>
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Files Impacted</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.files}</div>
              </div>
              <div className="bg-background rounded-lg p-4">
                <div className="text-gray-500 uppercase text-xs mb-1">Routes Impacted</div>
                <div className="text-2xl font-bold text-white">{impact.blast_radius.routes}</div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No graph entity selected for impact traversal.</p>
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
