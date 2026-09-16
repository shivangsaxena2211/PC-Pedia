import { Compass, Hammer, Sparkles } from 'lucide-react'

interface HeroSectionProps {
  productCount: number | null
  loading?: boolean
}

export default function HeroSection({ productCount, loading }: HeroSectionProps) {
  const eyebrow = loading
    ? 'Loading catalog statistics...'
    : productCount != null && productCount > 0
      ? `${productCount.toLocaleString()} verified components in catalog`
      : 'Growing hardware encyclopedia'

  return (
    <section className="hero" id="overview">
      <div className="hero-circuit" aria-hidden="true" />
      <div>
        <div className="hero-eyebrow">
          <Sparkles aria-hidden="true" />
          {eyebrow}
        </div>
        <h1>
          Explore the <span className="grad">World of PC Hardware</span>
        </h1>
        <p className="lead">
          Discover detailed specifications, compare components, and explore a verified
          hardware database backed by real catalog data.
        </p>
        <div className="hero-actions">
          <a href="#categories" className="btn btn-primary">
            <Compass aria-hidden="true" />
            Explore Hardware
          </a>
          <span className="btn btn-ghost" aria-disabled="true" title="PC Builder coming soon">
            <Hammer aria-hidden="true" />
            Build a PC
          </span>
        </div>
      </div>

      <div className="hero-visual" aria-hidden="true">
        <div className="hw-stack">
          <div className="hw-core">
            <div className="hw-core-inner">
              <img
                className="hw-core-logo"
                src="/images/pc-pedia-logo.png"
                alt=""
                width={140}
                height={88}
              />
            </div>
          </div>
          <div className="tag-float" style={{ top: '6%', left: '2%', animationDelay: '0s' }}>
            CPU <span>cores</span>
          </div>
          <div className="tag-float" style={{ top: '14%', right: '0%', animationDelay: '1.4s' }}>
            GPU <span>shader</span>
          </div>
          <div className="tag-float" style={{ bottom: '20%', left: '0%', animationDelay: '2.8s' }}>
            RAM <span>channels</span>
          </div>
          <div className="tag-float" style={{ bottom: '8%', right: '4%', animationDelay: '1s' }}>
            PCIe <span>lanes</span>
          </div>
          <div className="tag-float" style={{ top: '44%', left: '-4%', animationDelay: '3.5s' }}>
            NVMe <span>storage</span>
          </div>
        </div>
      </div>
    </section>
  )
}
