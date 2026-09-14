import { Link, Outlet, useLocation } from 'react-router-dom'
import { LayoutDashboard, Package, Building2, Layers, GitBranch, Plus } from 'lucide-react'
import { cn } from '@/lib/utils'

const ADMIN_NAV = [
  { label: 'Dashboard', path: '/admin', icon: LayoutDashboard },
  { label: 'Products', path: '/admin/products', icon: Package },
  { label: 'New Product', path: '/admin/products/new', icon: Plus },
  { label: 'Manufacturers', path: '/admin/manufacturers', icon: Building2 },
  { label: 'Series', path: '/admin/series', icon: Layers },
  { label: 'Generations', path: '/admin/generations', icon: GitBranch },
]

export default function AdminLayout() {
  const location = useLocation()

  return (
    <div className="mx-auto max-w-7xl px-4 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Panel</h1>
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        <aside className="lg:col-span-1">
          <nav className="space-y-1">
            {ADMIN_NAV.map((item) => {
              const Icon = item.icon
              const active = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
                    active
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary',
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </aside>
        <div className="lg:col-span-4">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
