import { Link } from 'react-router-dom'
import { Cpu } from 'lucide-react'

export default function LandingFooter() {
  return (
    <footer>
      <div className="footer-grid">
        <div className="footer-brand">
          <div className="logo">
            <div className="logo-mark">
              <Cpu aria-hidden="true" />
            </div>
            <span className="logo-text">PC PEDIA</span>
          </div>
          <p>The Encyclopedia of PC Hardware</p>
        </div>
        <div className="footer-links">
          <div className="footer-col">
            <h4>Product</h4>
            <a href="#categories">Hardware</a>
            <span style={{ display: 'block', color: 'var(--muted)', fontSize: '.87rem', padding: '6px 0' }}>
              PC Builder (coming soon)
            </span>
            <Link to="/compare">Compare</Link>
          </div>
          <div className="footer-col">
            <h4>Explore</h4>
            <Link to="/cpu">CPUs</Link>
            <Link to="/gpu">GPUs</Link>
            <Link to="/admin">Admin</Link>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <span>&copy; {new Date().getFullYear()} PC PEDIA</span>
        <span>Built for hardware enthusiasts</span>
      </div>
    </footer>
  )
}
