import { ArrowRight } from 'lucide-react'
import type { Product } from '@/types'
import { useReveal } from '@/hooks/useReveal'

interface PcBuilderPromoProps {
  sampleProducts: Product[]
}

const ROLE_LABELS = ['CPU', 'GPU', 'RAM', 'Storage', 'PSU'] as const

export default function PcBuilderPromo({ sampleProducts }: PcBuilderPromoProps) {
  const { ref, visible } = useReveal<HTMLDivElement>()
  const rows = ROLE_LABELS.map((role, index) => ({
    role,
    value: sampleProducts[index]?.name ?? '—',
  }))

  return (
    <section className="section" id="builder">
      <div ref={ref} className={`builder-card reveal${visible ? ' in' : ''}`}>
        <div>
          <h2>Build Your PC</h2>
          <p>
            Choose components, check compatibility, and explore the catalog. PC Builder
            tooling is coming soon — browse verified hardware in the meantime.
          </p>
          <span className="btn btn-primary" aria-disabled="true" title="Coming soon">
            Start Building <ArrowRight aria-hidden="true" />
          </span>
        </div>
        <div className="build-chain" aria-label="Example component slots">
          {rows.map((row) => (
            <div key={row.role} className="build-row">
              <div className="build-dot" aria-hidden="true" />
              <div className="build-role">{row.role}</div>
              <div className="build-val">{row.value}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
