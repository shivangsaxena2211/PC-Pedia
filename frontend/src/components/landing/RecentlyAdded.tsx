import { Link } from 'react-router-dom'
import type { Product } from '@/types'
import { getProductUrl } from '@/lib/utils'

interface RecentlyAddedProps {
  products: Product[]
}

function releaseYear(date?: string) {
  if (!date) return '—'
  const year = new Date(date).getFullYear()
  return Number.isNaN(year) ? '—' : String(year)
}

function socketOrInterface(product: Product) {
  const specs = product.quick_specs ?? {}
  return specs.Socket || specs.Interface || specs['Form Factor'] || '—'
}

export default function RecentlyAdded({ products }: RecentlyAddedProps) {
  if (products.length === 0) {
    return (
      <section className="section" id="recent">
        <div className="section-head">
          <div>
            <h2>Recently Added Hardware</h2>
            <p>Newest components indexed in the database</p>
          </div>
        </div>
        <p style={{ color: 'var(--muted)' }}>No recent products to display.</p>
      </section>
    )
  }

  return (
    <section className="section" id="recent">
      <div className="section-head">
        <div>
          <h2>Recently Added Hardware</h2>
          <p>Newest components indexed in the database</p>
        </div>
      </div>
      <div className="glass table-wrap">
        <table className="hw-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Model</th>
              <th>Generation</th>
              <th>Socket / Interface</th>
              <th>Release Year</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>
                  <span className="pill-comp">
                    <span className="dot" aria-hidden="true" />
                    {product.category || '—'}
                  </span>
                </td>
                <td>
                  <Link to={getProductUrl(product)}>{product.name}</Link>
                </td>
                <td>{product.generation || '—'}</td>
                <td>{socketOrInterface(product)}</td>
                <td>{releaseYear(product.release_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="row-cards">
          {products.map((product) => (
            <div key={product.id} className="row-card glass">
              <div className="row-card-top">
                <span className="pill-comp">
                  <span className="dot" aria-hidden="true" />
                  {product.category}
                </span>
                <span style={{ color: 'var(--muted)', fontSize: '.78rem' }}>
                  {releaseYear(product.release_date)}
                </span>
              </div>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>
                <Link to={getProductUrl(product)}>{product.name}</Link>
              </div>
              <div className="row-card-grid">
                <div>Generation: <b>{product.generation || '—'}</b></div>
                <div>Interface: <b>{socketOrInterface(product)}</b></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
