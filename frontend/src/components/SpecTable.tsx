import type { Specification } from '@/types'

interface SpecTableProps {
  groups: Record<string, Specification[]>
}

export default function SpecTable({ groups }: SpecTableProps) {
  return (
    <div className="product-spec-groups space-y-8">
      {Object.entries(groups).map(([groupName, specs]) => (
        <section key={groupName} className="product-spec-group">
          <h3 className="product-spec-group-title text-sm font-semibold text-primary uppercase tracking-wider">
            {groupName}
          </h3>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="product-spec-table w-full text-sm">
              <tbody>
                {specs.map((spec, i) => (
                  <tr
                    key={spec.id}
                    className={i % 2 === 0 ? 'bg-card' : 'bg-muted/30'}
                  >
                    <td className="product-spec-label font-medium text-muted-foreground w-1/3 border-r border-border">
                      {spec.display_name || spec.key}
                    </td>
                    <td className="product-spec-value">
                      {spec.value}
                      {spec.unit && <span className="text-muted-foreground ml-1">{spec.unit}</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  )
}
