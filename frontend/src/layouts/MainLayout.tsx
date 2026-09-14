import { Outlet } from 'react-router-dom'
import Navbar from '@/components/Navbar'

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-border py-8 mt-auto">
        <div className="mx-auto max-w-7xl px-4 lg:px-8 text-center text-sm text-muted-foreground">
          <p>PC Hardware Database &mdash; Explore. Compare. Understand.</p>
          <p className="mt-1 text-xs">A comprehensive encyclopedia for computer hardware.</p>
        </div>
      </footer>
    </div>
  )
}
