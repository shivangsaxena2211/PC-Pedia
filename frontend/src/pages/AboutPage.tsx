import { useCallback, useEffect, useRef, useState, type CSSProperties } from 'react'
import { Link } from 'react-router-dom'
import './about.css'

const LOGO_SRC = '/pc-pedia-intro-logo.png'

type Frag = {
  label: string
  type: 'category' | 'spec'
  cluster: string
  sx: number
  sy: number
  ox: number
  oy: number
}

const FRAGS: Frag[] = [
  { label: 'CPU', type: 'category', cluster: 'cpu', sx: 14, sy: 22, ox: 24, oy: 40 },
  { label: 'CORES', type: 'spec', cluster: 'cpu', sx: 8, sy: 58, ox: 12, oy: 36 },
  { label: 'THREADS', type: 'spec', cluster: 'cpu', sx: 22, sy: 78, ox: 14, oy: 52 },
  { label: 'CLOCK', type: 'spec', cluster: 'cpu', sx: 6, sy: 38, ox: 28, oy: 58 },
  { label: 'CACHE', type: 'spec', cluster: 'cpu', sx: 30, sy: 12, ox: 34, oy: 48 },
  { label: 'GPU', type: 'category', cluster: 'gpu', sx: 86, sy: 24, ox: 76, oy: 40 },
  { label: 'VRAM', type: 'spec', cluster: 'gpu', sx: 92, sy: 56, ox: 88, oy: 36 },
  { label: 'MEMORY', type: 'spec', cluster: 'gpu', sx: 78, sy: 80, ox: 86, oy: 52 },
  { label: 'TDP', type: 'spec', cluster: 'gpu', sx: 94, sy: 38, ox: 72, oy: 58 },
  { label: 'PCIe', type: 'spec', cluster: 'gpu', sx: 70, sy: 10, ox: 66, oy: 48 },
  { label: 'RAM', type: 'category', cluster: 'misc', sx: 50, sy: 8, ox: 20, oy: 16 },
  { label: 'MOTHERBOARD', type: 'category', cluster: 'misc', sx: 46, sy: 90, ox: 38, oy: 14 },
  { label: 'STORAGE', type: 'category', cluster: 'misc', sx: 60, sy: 92, ox: 56, oy: 12 },
  { label: 'COOLING', type: 'category', cluster: 'misc', sx: 4, sy: 14, ox: 70, oy: 15 },
  { label: 'SPECIFICATIONS', type: 'category', cluster: 'misc', sx: 96, sy: 14, ox: 80, oy: 18 },
  { label: 'GENERATIONS', type: 'category', cluster: 'misc', sx: 38, sy: 50, ox: 50, oy: 22 },
]

const LINK_PAIRS: [string, string][] = [
  ['CPU', 'CORES'],
  ['CPU', 'THREADS'],
  ['CPU', 'CLOCK'],
  ['CPU', 'CACHE'],
  ['GPU', 'VRAM'],
  ['GPU', 'MEMORY'],
  ['GPU', 'TDP'],
  ['GPU', 'PCIe'],
]

const PILLS = ['CPU', 'GPU', 'RAM', 'MOTHERBOARD', 'STORAGE', 'COMPARE'] as const

type Particle = {
  x: number
  y: number
  r: number
  vx: number
  vy: number
  a: number
  tw: number
}

type TimelineStep = {
  t: number
  cls: string
  remove?: string[]
  startPills?: boolean
  stopPills?: boolean
}

const TIMELINE: TimelineStep[] = [
  { t: 0, cls: 'stage-active' },
  { t: 0, cls: 'phase-1' },
  { t: 3000, cls: 'phase-2', remove: ['phase-1'] },
  { t: 7000, cls: 'phase-3', remove: ['phase-2'] },
  { t: 11000, cls: 'phase-4', remove: ['phase-3'], startPills: true },
  { t: 15000, cls: 'phase-5', remove: ['phase-4'], stopPills: true },
  { t: 18000, cls: 'phase-6', remove: ['phase-5'] },
  { t: 20500, cls: 'show-replay' },
]

function fragByLabel(label: string): Frag {
  const found = FRAGS.find((f) => f.label === label)
  if (!found) throw new Error(`Missing fragment: ${label}`)
  return found
}

export default function AboutPage() {
  const rootRef = useRef<HTMLDivElement>(null)
  const stageRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [phaseClasses, setPhaseClasses] = useState('pc-pedia-about')
  const [activePill, setActivePill] = useState(0)
  const [replayKey, setReplayKey] = useState(0)
  const timersRef = useRef<number[]>([])
  const pillIntervalRef = useRef<number | null>(null)

  const clearTimers = useCallback(() => {
    timersRef.current.forEach((id) => window.clearTimeout(id))
    timersRef.current = []
  }, [])

  const stopPillCycle = useCallback(() => {
    if (pillIntervalRef.current !== null) {
      window.clearInterval(pillIntervalRef.current)
      pillIntervalRef.current = null
    }
    setActivePill(0)
  }, [])

  const startPillCycle = useCallback(() => {
    stopPillCycle()
    let idx = 0
    setActivePill(0)
    pillIntervalRef.current = window.setInterval(() => {
      idx = (idx + 1) % PILLS.length
      setActivePill(idx)
    }, 1000)
  }, [stopPillCycle])

  const playIntro = useCallback(() => {
    clearTimers()
    stopPillCycle()
    setPhaseClasses('pc-pedia-about')
    setReplayKey((k) => k + 1)

    // Wait for React to paint the reset class, then reflow + schedule phases
    // so CSS transitions restart cleanly (matches original body.className reset).
    const startId = window.setTimeout(() => {
      void rootRef.current?.offsetWidth
      TIMELINE.forEach((step) => {
        const id = window.setTimeout(() => {
          setPhaseClasses((prev) => {
            const parts = new Set(prev.split(/\s+/).filter(Boolean))
            parts.add('pc-pedia-about')
            step.remove?.forEach((c) => parts.delete(c))
            parts.add(step.cls)
            return Array.from(parts).join(' ')
          })
          if (step.startPills) startPillCycle()
          if (step.stopPills) stopPillCycle()
        }, step.t)
        timersRef.current.push(id)
      })
    }, 0)
    timersRef.current.push(startId)
  }, [clearTimers, startPillCycle, stopPillCycle])

  useEffect(() => {
    playIntro()
    return () => {
      clearTimers()
      stopPillCycle()
    }
    // Intentionally mount-only: replay is handled by button via playIntro.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  /* Ambient particle canvas */
  useEffect(() => {
    const canvas = canvasRef.current
    const stage = stageRef.current
    if (!canvas || !stage) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let W = 0
    let H = 0
    const DPR = Math.min(window.devicePixelRatio || 1, 2)
    const particles: Particle[] = []
    let raf = 0
    const t0 = performance.now()

    const resize = () => {
      W = stage.clientWidth
      H = stage.clientHeight
      canvas.width = W * DPR
      canvas.height = H * DPR
      canvas.style.width = `${W}px`
      canvas.style.height = `${H}px`
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0)
    }

    resize()
    window.addEventListener('resize', resize)

    const PARTICLE_COUNT = 55
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * Math.max(W, 1),
        y: Math.random() * Math.max(H, 1),
        r: Math.random() * 1.4 + 0.4,
        vx: (Math.random() - 0.5) * 0.1,
        vy: (Math.random() - 0.5) * 0.1,
        a: Math.random() * 0.5 + 0.15,
        tw: Math.random() * Math.PI * 2,
      })
    }

    const tick = (now: number) => {
      ctx.clearRect(0, 0, W, H)
      const elapsed = (now - t0) / 1000
      for (const p of particles) {
        p.x += p.vx
        p.y += p.vy
        if (p.x < -5) p.x = W + 5
        if (p.x > W + 5) p.x = -5
        if (p.y < -5) p.y = H + 5
        if (p.y > H + 5) p.y = -5
        const flicker = 0.6 + 0.4 * Math.sin(elapsed * 1.4 + p.tw)
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(196,181,253,${(p.a * flicker).toFixed(3)})`
        ctx.fill()
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(raf)
    }
  }, [replayKey])

  return (
    <div ref={rootRef} className={phaseClasses}>
      <div className="about-viewport">
        <div className="about-stage" ref={stageRef}>
          <canvas className="about-bg-canvas" ref={canvasRef} aria-hidden="true" />
          <div className="about-grid" />
          <div className="about-blob about-blob-a" />
          <div className="about-blob about-blob-b" />
          <div className="about-blob about-blob-c" />
          <div className="about-streak about-streak-1" />
          <div className="about-streak about-streak-2" />
          <div className="about-streak about-streak-3" />

          <svg className="about-links" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="about-linkGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#c4b5fd" />
                <stop offset="100%" stopColor="#6d28d9" />
              </linearGradient>
            </defs>
            {LINK_PAIRS.map(([a, b], i) => {
              const fa = fragByLabel(a)
              const fb = fragByLabel(b)
              return (
                <path
                  key={`${a}-${b}`}
                  d={`M ${fa.ox} ${fa.oy} L ${fb.ox} ${fb.oy}`}
                  style={{ transitionDelay: `${i * 0.05}s` }}
                />
              )
            })}
          </svg>

          <div className="about-fragments">
            {FRAGS.map((f, i) => (
              <div
                key={f.label}
                className={`about-frag ${f.type}`}
                style={
                  {
                    '--sx': `${f.sx}%`,
                    '--sy': `${f.sy}%`,
                    '--ox': `${f.ox}%`,
                    '--oy': `${f.oy}%`,
                  } as CSSProperties
                }
              >
                <div className="inner" style={{ animationDelay: `${i * 0.18}s` }}>
                  {f.label}
                </div>
              </div>
            ))}
          </div>

          <div className="about-panel-wrap">
            <div className="about-panel">
              <div className="about-panel-head">
                <svg className="mark" viewBox="0 0 120 120" fill="none" aria-hidden="true">
                  <use href="#about-pcpedia-mark" />
                </svg>
                <div className="word">PC&nbsp;PEDIA</div>
              </div>
              <div className="about-search-bar">
                <svg viewBox="0 0 24 24" fill="none" stroke="#b7abd6" strokeWidth="2" aria-hidden="true">
                  <circle cx="11" cy="11" r="7" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <span>
                  Search hardware, specs, generations
                  <span className="about-search-caret" />
                </span>
              </div>
              <div className="about-pill-row">
                {PILLS.map((pill, i) => (
                  <div key={pill} className={`pill${activePill === i ? ' on' : ''}`}>
                    {pill}
                  </div>
                ))}
              </div>
              <div className="about-card-viewport">
                <div className="about-spec-card about-card-1">
                  <div className="label">CPU</div>
                  <div className="title">Processor</div>
                  <div className="fields">
                    <span>Architecture</span>
                    <span>Cores</span>
                    <span>Threads</span>
                    <span>Clock</span>
                    <span>Cache</span>
                  </div>
                </div>
                <div className="about-spec-card about-card-2">
                  <div className="label">GPU</div>
                  <div className="title">Graphics</div>
                  <div className="fields">
                    <span>Architecture</span>
                    <span>VRAM</span>
                    <span>Memory</span>
                    <span>Core Count</span>
                    <span>Power</span>
                  </div>
                </div>
                <div className="about-spec-card about-card-3">
                  <div className="label">RAM &amp; MOTHERBOARD</div>
                  <div className="title">Platform</div>
                  <div className="fields">
                    <span>Capacity</span>
                    <span>Speed</span>
                    <span>Chipset</span>
                    <span>Form Factor</span>
                  </div>
                </div>
                <div className="about-spec-card about-card-4">
                  <div className="label">COMPARE</div>
                  <div className="title">Side by Side</div>
                  <div className="fields">
                    <span>Generation</span>
                    <span>Specifications</span>
                    <span>Value</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="about-brand">
            <div className="about-logo-burst" />
            <div className="about-logo-glow" />
            <div className="about-logo-wrap">
              <img className="about-logo-mark" src={LOGO_SRC} alt="PC Pedia logo" />
              <div
                className="about-logo-shine"
                style={{ ['--logo-mask' as string]: `url("${LOGO_SRC}")` }}
              />
            </div>
            <div className="about-brand-title">PC PEDIA</div>
            <div className="about-brand-tagline">The Encyclopedia of PC Hardware</div>
            <div className="about-brand-sub">Explore. Compare. Build.</div>
          </div>

          <div className="about-vignette" />
          <div className="about-grain" />

          <div className="about-cta-row">
            <Link to="/" className="about-enter">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M5 12h14" />
                <path d="M13 5l7 7-7 7" />
              </svg>
              EXPLORE PC PEDIA
            </Link>
            <button type="button" className="about-replay" onClick={playIntro}>
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M1 4v6h6" />
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
              </svg>
              REPLAY
            </button>
          </div>
          <div className="about-skip-hint"></div>
        </div>
      </div>

      <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
        <defs>
          <g id="about-pcpedia-mark">
            <linearGradient id="about-markGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#efe7ff" />
              <stop offset="55%" stopColor="#a78bfa" />
              <stop offset="100%" stopColor="#6d28d9" />
            </linearGradient>
            <g stroke="url(#about-markGrad)" strokeWidth="3" strokeLinecap="round">
              <line x1="36" y1="8" x2="36" y2="20" />
              <line x1="60" y1="6" x2="60" y2="20" />
              <line x1="84" y1="8" x2="84" y2="20" />
              <line x1="36" y1="100" x2="36" y2="112" />
              <line x1="60" y1="100" x2="60" y2="114" />
              <line x1="84" y1="100" x2="84" y2="112" />
              <line x1="8" y1="36" x2="20" y2="36" />
              <line x1="6" y1="60" x2="20" y2="60" />
              <line x1="8" y1="84" x2="20" y2="84" />
              <line x1="100" y1="36" x2="112" y2="36" />
              <line x1="114" y1="60" x2="100" y2="60" />
              <line x1="100" y1="84" x2="112" y2="84" />
            </g>
            <rect
              x="20"
              y="20"
              width="80"
              height="80"
              rx="16"
              fill="rgba(139,92,246,0.10)"
              stroke="url(#about-markGrad)"
              strokeWidth="3"
            />
            <path d="M100 20 L100 40 L80 20 Z" fill="url(#about-markGrad)" opacity="0.9" />
            <path
              d="M46 38 L46 82 M46 38 L64 38 Q76 38 76 50 Q76 62 64 62 L46 62"
              fill="none"
              stroke="url(#about-markGrad)"
              strokeWidth="6.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </g>
        </defs>
      </svg>
    </div>
  )
}
