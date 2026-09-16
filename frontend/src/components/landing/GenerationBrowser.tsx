import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { Generation } from '@/types'

interface GenerationBrowserProps {
  intelGenerations: Generation[]
  amdGenerations: Generation[]
}

type VendorTab = 'intel' | 'amd'

function generationLink(gen: Generation, manufacturer: string) {
  const params = new URLSearchParams()
  params.set('generation', gen.slug)
  params.set('manufacturer', manufacturer)
  return `/cpu?${params.toString()}`
}

export default function GenerationBrowser({
  intelGenerations,
  amdGenerations,
}: GenerationBrowserProps) {
  const [tab, setTab] = useState<VendorTab>('intel')
  const generations = tab === 'intel' ? intelGenerations : amdGenerations

  return (
    <section className="section" id="generations">
      <div className="section-head">
        <div>
          <h2>Browse by Generation</h2>
          <p>Jump to a CPU generation in the verified catalog</p>
        </div>
      </div>

      <div className="gen-tabs" role="tablist" aria-label="CPU vendor">
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'intel'}
          className={`gen-tab${tab === 'intel' ? ' active' : ''}`}
          onClick={() => setTab('intel')}
        >
          Intel
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === 'amd'}
          className={`gen-tab${tab === 'amd' ? ' active' : ''}`}
          onClick={() => setTab('amd')}
        >
          AMD Ryzen
        </button>
      </div>

      <div className="gen-pills show" role="tabpanel">
        {generations.length === 0 ? (
          <p style={{ color: 'var(--muted)', fontSize: '.9rem' }}>
            No generations available for this vendor yet.
          </p>
        ) : (
          generations.map((gen) => (
            <Link
              key={gen.id}
              to={generationLink(gen, tab === 'intel' ? 'intel' : 'amd')}
              className="gen-pill"
            >
              {gen.name.replace(' Generation', ' Gen').replace('Ryzen ', 'Ryzen ')}
            </Link>
          ))
        )}
      </div>
    </section>
  )
}
