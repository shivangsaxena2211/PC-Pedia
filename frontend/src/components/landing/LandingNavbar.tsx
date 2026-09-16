import { Link } from 'react-router-dom'
import { Menu, GitCompare, Search } from 'lucide-react'
import LandingSearch from './LandingSearch'

interface LandingNavbarProps {
  onOpenMobileSidebar: () => void
  mobileSearchOpen: boolean
  onToggleMobileSearch: () => void
  onCloseMobileSearch: () => void
}

export default function LandingNavbar({
  onOpenMobileSidebar,
  mobileSearchOpen,
  onToggleMobileSearch,
  onCloseMobileSearch,
}: LandingNavbarProps) {
  return (
    <header className="navbar">
      <button
        type="button"
        className="hamburger"
        onClick={onOpenMobileSidebar}
        aria-label="Open menu"
      >
        <Menu aria-hidden="true" />
      </button>

      <div className="navbar-title">
        <h1>Hardware Encyclopedia</h1>
        <p>Explore, compare and understand PC hardware</p>
      </div>

      <LandingSearch
        showKbd
        mobileShow={mobileSearchOpen}
        onCloseMobile={onCloseMobileSearch}
      />

      <button
        type="button"
        className="nb-btn search-toggle-mobile"
        onClick={onToggleMobileSearch}
        aria-label="Search"
      >
        <Search aria-hidden="true" />
      </button>

      <div className="navbar-actions">
        <Link to="/compare" className="nb-btn">
          <GitCompare aria-hidden="true" />
          <span>Compare</span>
        </Link>
        <div className="nb-avatar" aria-hidden="true">PC</div>
      </div>
    </header>
  )
}
