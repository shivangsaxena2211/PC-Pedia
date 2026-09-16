import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { Product } from '@/types'
import { getProductUrl } from '@/lib/utils'

interface FeaturedHardwareProps {
  products: Product[]
}

function getSpecPairs(product: Product): { key: string; value: string }[] {
  const specs = product.quick_specs ?? {}
  const priority = [
    'Total Cores', 'Threads', 'Maximum Boost Clock', 'Base Clock',
    'TDP', 'Socket', 'VRAM', 'Capacity', 'Wattage',
  ]
  const pairs: { key: string; value: string }[] = []

  for (const key of priority) {
    if (specs[key]) pairs.push({ key, value: specs[key] })
    if (pairs.length >= 4) break
  }

  if (pairs.length < 2) {
    for (const [key, value] of Object.entries(specs)) {
      if (!pairs.find((p) => p.key === key)) {
        pairs.push({ key, value })
        if (pairs.length >= 4) break
      }
    }
  }

  return pairs.slice(0, 4)
}

export default function FeaturedHardware({ products }: FeaturedHardwareProps) {
  if (products.length === 0) {
    return (
      <section className="section" id="featured">
        <div className="section-head">
          <div>
            <h2>Featured Hardware</h2>
            <p>Popular products from the verified catalog</p>
          </div>
        </div>
        <p style={{ color: 'var(--muted)' }}>No featured products available yet.</p>
      </section>
    )
  }

  return (
    <section className="section" id="featured">
      <div className="section-head">
        <div>
          <h2>Featured Hardware</h2>
          <p>Popular products from the verified catalog</p>
        </div>
        <Link to="/cpu" className="section-link">
          View CPUs <ArrowRight aria-hidden="true" />
        </Link>
      </div>
      <div className="feat-scroll">
        {products.map((product) => {
          const specs = getSpecPairs(product)
          return (
            <Link
              key={product.id}
              to={getProductUrl(product)}
              className="feat-card glass"
            >
              <div className="feat-top">
                <span className="feat-type">{product.category || 'Hardware'}</span>
                <span className="feat-badge">{product.manufacturer}</span>
              </div>
              <h3>{product.name}</h3>
              <div className="feat-specs">
                {specs.map(({ key, value }) => (
                  <div key={key} className="feat-spec">
                    <div className="k">{key}</div>
                    <div className="v">{value}</div>
                  </div>
                ))}
              </div>
              <div className="feat-bottom">
                <span className="feat-btn">
                  View Details <ArrowRight aria-hidden="true" />
                </span>
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
