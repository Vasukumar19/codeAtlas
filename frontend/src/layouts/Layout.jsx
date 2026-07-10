import { Outlet } from 'react-router-dom'
import { LeftSidebar } from './LeftSidebar'
import { RightInspector } from './RightInspector'

export function Layout() {
  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <LeftSidebar />
      <main className="flex-1 relative border-l border-r border-border">
        <Outlet />
      </main>
      <RightInspector />
    </div>
  )
}
