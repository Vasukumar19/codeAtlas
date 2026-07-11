import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/layouts/Layout'
import { Landing } from '@/pages/Landing'
import { Dashboard } from '@/pages/Dashboard'
import { ImportPipeline } from '@/pages/ImportPipeline'
import { ExecutionFlow } from '@/features/execution/ExecutionFlowPlayer'
import Analysis from '@/pages/Analysis'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/import" element={<ImportPipeline />} />
          <Route element={<Layout />}>
            <Route path="/repo/:id" element={<Dashboard />} />
            <Route path="/repo/:id/flow" element={<ExecutionFlow />} />
            <Route path="/repo/:id/analysis" element={<Analysis />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
