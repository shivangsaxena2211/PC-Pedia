import type { Specification } from '@/types'

interface SpecTableProps {
  groups: Record<string, Specification[]>
}

export default function SpecTable({ groups }: SpecTableProps) {
  return (
    <div className="space-y-6">
      {Object.entries(groups).map(([groupName, specs]) => (
        <div key={groupName}>
          <h3 className="text-sm font-semibold text-primary mb-3 uppercase tracking-wider">
            {groupName}
          </h3>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <tbody>
                {specs.map((spec, i) => (
                  <tr
                    key={spec.id}
                    className={i % 2 === 0 ? 'bg-card' : 'bg-muted/30'}
                  >
                    <td className="px-4 py-3 font-medium text-muted-foreground w-1/3 border-r border-border">
                      {spec.key}
                    </td>
                    <td className="px-4 py-3">
                      {spec.value}
                      {spec.unit && <span className="text-muted-foreground ml-1">{spec.unit}</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}
