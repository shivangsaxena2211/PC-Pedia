import { useReveal } from '@/hooks/useReveal'
import { useAnimatedCounter } from '@/hooks/useAnimatedCounter'

interface StatItem {
  value: number | null
  label: string
  suffix?: string
}

interface StatsStripProps {
  stats: StatItem[]
  loading?: boolean
  error?: string | null
}

function StatCell({
  value,
  label,
  suffix = '',
  active,
  loading,
  unavailable,
}: StatItem & { active: boolean; loading?: boolean; unavailable?: boolean }) {
  const count = useAnimatedCounter(value ?? 0, active && value != null)
  let display = '—'

  if (loading) {
    display = '…'
  } else if (unavailable || value == null) {
    display = '—'
  } else {
    display = suffix && count >= value ? `${value}${suffix}` : `${count}${suffix}`
  }

  return (
    <div className="stat-cell">
      <div className="stat-num">{display}</div>
      <div className="stat-lbl">{label}</div>
    </div>
  )
}

export default function StatsStrip({ stats, loading, error }: StatsStripProps) {
  const { ref, visible } = useReveal<HTMLDivElement>()

  return (
    <div ref={ref} className={`stats-strip reveal${visible ? ' in' : ''}`}>
      {stats.map((stat) => (
        <StatCell
          key={stat.label}
          {...stat}
          active={visible && !loading && stat.value != null}
          loading={loading}
          unavailable={Boolean(error) || stat.value == null}
        />
      ))}
    </div>
  )
}
