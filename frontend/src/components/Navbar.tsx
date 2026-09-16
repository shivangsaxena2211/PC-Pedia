import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Search, Cpu } from 'lucide-react'
import { useCategories } from '@/hooks/useCategories'
import { cn, getCategoryPath } from '@/lib/utils'
import SearchBar from './SearchBar'

const STATIC_NAV = [
  { label: 'Home', path: '/' },
  { label: 'Compare', path: '/compare' },
]

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const location = useLocation()
  const { categories } = useCategories()

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight">
          <Cpu className="h-6 w-6 text-primary" />
          <span className="hidden sm:inline">PC PEDIA</span>
        </Link>

        <div className="hidden lg:flex items-center gap-4 overflow-x-auto">
          {STATIC_NAV.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'px-4 py-2.5 text-sm font-medium tracking-wide transition-colors rounded-md whitespace-nowrap',
                isActive(item.path)
                  ? 'text-primary bg-primary/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary',
              )}
            >
              {item.label}
            </Link>
          ))}
          {categories.map((cat) => (
            <Link
              key={cat.slug}
              to={getCategoryPath(cat.slug)}
              className={cn(
                'px-4 py-2.5 text-sm font-medium tracking-wide transition-colors rounded-md whitespace-nowrap',
                isActive(getCategoryPath(cat.slug))
                  ? 'text-primary bg-primary/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-secondary',
              )}
            >
              {cat.name === 'Motherboard' ? 'Motherboards' : cat.name === 'CPU Cooler' ? 'Coolers' : cat.name}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="p-2.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </button>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {searchOpen && (
        <div className="border-t border-border px-4 py-3 lg:px-8">
          <SearchBar onClose={() => setSearchOpen(false)} />
        </div>
      )}

      {mobileOpen && (
        <div className="lg:hidden border-t border-border bg-background max-h-[70vh] overflow-y-auto">
          <div className="flex flex-col p-4 gap-2">
            {STATIC_NAV.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'px-4 py-3 text-sm font-medium rounded-md transition-colors',
                  isActive(item.path)
                    ? 'text-primary bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary',
                )}
              >
                {item.label}
              </Link>
            ))}
            {categories.map((cat) => (
              <Link
                key={cat.slug}
                to={getCategoryPath(cat.slug)}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'px-4 py-3 text-sm font-medium rounded-md transition-colors',
                  isActive(getCategoryPath(cat.slug))
                    ? 'text-primary bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary',
                )}
              >
                {cat.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  )
}
