import { Link, useLocation } from 'react-router-dom'
import {
  Cpu, Monitor, CircuitBoard, MemoryStick, Database, Zap, Fan, Server, Wind,
  LayoutDashboard, Hammer, ShieldCheck, GitCompare, Gauge, PanelLeftClose,
  Settings, Info,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { getCategoryPath } from '@/lib/utils'
import type { Category } from '@/types'

interface NavItem {
  label: string
  path?: string
  icon: LucideIcon
  disabled?: boolean
  sectionId?: string
}

const CATEGORY_ICONS: Record<string, LucideIcon> = {
  cpu: Cpu,
  gpu: Monitor,
  motherboards: CircuitBoard,
  ram: MemoryStick,
  ssd: Database,
  psu: Zap,
  coolers: Fan,
  cases: Server,
  fans: Wind,
  aio: Fan,
}

const TOOL_ITEMS: NavItem[] = [
  { label: 'PC Builder', icon: Hammer, disabled: true },
  { label: 'Compatibility Checker', icon: ShieldCheck, disabled: true },
  { label: 'Compare Hardware', icon: GitCompare, path: '/compare' },
  { label: 'Bottleneck Calculator', icon: Gauge, disabled: true },
]

interface LandingSidebarProps {
  categories: Category[]
  collapsed: boolean
  mobileOpen: boolean
  onToggle: () => void
  onNavigate: () => void
}

function NavLinkItem({
  item,
  active,
  collapsed,
  onNavigate,
}: {
  item: NavItem
  active: boolean
  collapsed: boolean
  onNavigate: () => void
}) {
  const Icon = item.icon
  const className = `nav-item${active ? ' active' : ''}${item.disabled ? ' nav-item-disabled' : ''}`

  if (item.disabled || !item.path) {
    return (
      <span className={className} aria-disabled="true" title="Coming soon">
        <Icon aria-hidden="true" />
        {!collapsed && <span>{item.label}</span>}
      </span>
    )
  }

  return (
    <Link to={item.path} className={className} onClick={onNavigate}>
      <Icon aria-hidden="true" />
      {!collapsed && <span>{item.label}</span>}
    </Link>
  )
}

export default function LandingSidebar({
  categories,
  collapsed,
  mobileOpen,
  onToggle,
  onNavigate,
}: LandingSidebarProps) {
  const location = useLocation()
  const isHome = location.pathname === '/'

  const exploreItems: NavItem[] = [
    { label: 'Overview', path: '/', icon: LayoutDashboard },
    ...categories.map((cat) => ({
      label: cat.name === 'Motherboard' ? 'Motherboards' : cat.name === 'CPU Cooler' ? 'CPU Coolers' : cat.name,
      path: getCategoryPath(cat.slug),
      icon: CATEGORY_ICONS[cat.slug] ?? Cpu,
    })),
  ]

  return (
    <aside className={`sidebar${collapsed ? ' collapsed' : ''}${mobileOpen ? ' mobile-open' : ''}`}>
      <div className="sidebar-head">
        <Link to="/" className="logo" onClick={onNavigate}>
          <div className="logo-mark">
            <Cpu aria-hidden="true" />
          </div>
          <span className="logo-text">PC PEDIA</span>
        </Link>
        <button
          type="button"
          className="sidebar-toggle"
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <PanelLeftClose aria-hidden="true" />
        </button>
      </div>

      <nav className="sidebar-body" aria-label="Main navigation">
        <div className="nav-group">
          <div className="nav-label">Explore</div>
          {exploreItems.map((item) => (
            <NavLinkItem
              key={item.label}
              item={item}
              active={item.path === '/' ? isHome : location.pathname === item.path}
              collapsed={collapsed}
              onNavigate={onNavigate}
            />
          ))}
        </div>

        <div className="nav-group">
          <div className="nav-label">Tools</div>
          {TOOL_ITEMS.map((item) => (
            <NavLinkItem
              key={item.label}
              item={item}
              active={item.path ? location.pathname === item.path : false}
              collapsed={collapsed}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      </nav>

      <div className="sidebar-foot">
        <span className="nav-item nav-item-disabled" aria-disabled="true" title="Coming soon">
          <Settings aria-hidden="true" />
          {!collapsed && <span>Settings</span>}
        </span>
        <Link to="/cpu" className="nav-item" onClick={onNavigate}>
          <Info aria-hidden="true" />
          {!collapsed && <span>About PC PEDIA</span>}
        </Link>
      </div>
    </aside>
  )
}
