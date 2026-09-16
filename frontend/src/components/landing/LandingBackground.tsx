import { useState } from 'react'

function createParticles() {
  return Array.from({ length: 24 }, (_, i) => ({
    id: i,
    size: 1.5 + ((i * 17) % 25) / 10,
    left: ((i * 37) % 100),
    top: 60 + ((i * 23) % 40),
    duration: 16 + ((i * 11) % 20),
    delay: (i * 7) % 20,
  }))
}

export default function LandingBackground() {
  const [particles] = useState(createParticles)

  return (
    <div className="bg-layer" aria-hidden="true">
      <div className="bg-grid" />
      <div className="bg-blob blob-1" />
      <div className="bg-blob blob-2" />
      <div className="bg-blob blob-3" />
      <div className="bg-lines">
        <div className="bg-line" />
        <div className="bg-line" />
        <div className="bg-line" />
      </div>
      <div id="particles">
        {particles.map((p) => (
          <div
            key={p.id}
            className="particle"
            style={{
              width: `${p.size}px`,
              height: `${p.size}px`,
              left: `${p.left}vw`,
              top: `${p.top}vh`,
              animationDuration: `${p.duration}s`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
