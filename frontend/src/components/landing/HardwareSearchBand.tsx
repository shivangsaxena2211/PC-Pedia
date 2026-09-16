import { Link } from 'react-router-dom'
import LandingSearch from './LandingSearch'
import { useReveal } from '@/hooks/useReveal'
import { getCategoryPath } from '@/lib/utils'

const QUICK_CATEGORIES = [
  { label: 'CPU', slug: 'cpu' },
  { label: 'GPU', slug: 'gpu' },
  { label: 'RAM', slug: 'ram' },
  { label: 'Motherboard', slug: 'motherboards' },
  { label: 'SSD', slug: 'ssd' },
  { label: 'PSU', slug: 'psu' },
  { label: 'Cooler', slug: 'coolers' },
  { label: 'Case', slug: 'cases' },
]

export default function HardwareSearchBand() {
  const { ref, visible } = useReveal<HTMLDivElement>()

  return (
    <section className="section">
      <div ref={ref} className={`glass search-band reveal${visible ? ' in' : ''}`}>
        <h2>What hardware are you looking for?</h2>
        <p>Search across the PC PEDIA hardware database</p>
        <LandingSearch
          variant="band"
          placeholder="Search the PC PEDIA hardware database..."
        />
        <div className="search-cats">
          {QUICK_CATEGORIES.map((cat) => (
            <Link key={cat.slug} to={getCategoryPath(cat.slug)} className="search-cat">
              {cat.label}
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}
