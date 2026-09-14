import { Fragment } from 'react'
import type { ComparisonResponse } from '@/types'
import { cn } from '@/lib/utils'

interface ComparisonTableProps {
  data: ComparisonResponse
}

export default function ComparisonTable({ data }: ComparisonTableProps) {
  const { products, comparison } = data

  const grouped = comparison.reduce<Record<string, typeof comparison>>((acc, row) => {
    if (!acc[row.group]) acc[row.group] = []
    acc[row.group].push(row)
    return acc
  }, {})

  return (
    <div className="space-y-8">
      <div className="overflow-x-auto">
        <table className="w-full text-sm border border-border rounded-lg overflow-hidden">
          <thead>
            <tr className="bg-muted">
              <th className="px-4 py-3 text-left font-semibold border-b border-border w-48">
                Specification
              </th>
              {products.map((p) => (
                <th key={p.slug} className="px-4 py-3 text-left font-semibold border-b border-border min-w-[200px]">
                  <div className="text-primary">{p.name}</div>
                  <div className="text-xs text-muted-foreground font-normal mt-0.5">
                    {p.manufacturer}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(grouped).map(([group, rows]) => (
              <Fragment key={group}>
                <tr className="bg-secondary/50">
                  <td
                    colSpan={products.length + 1}
                    className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-primary"
                  >
                    {group}
                  </td>
                </tr>
                {rows.map((row) => (
                  <tr
                    key={`${row.group}-${row.key}`}
                    className={cn(
                      'border-b border-border hover:bg-muted/20',
                      !row.all_same && 'bg-primary/5',
                    )}
                  >
                    <td className="px-4 py-3 font-medium text-muted-foreground">
                      {row.display_name || row.key}
                    </td>
                    {products.map((p) => (
                      <td
                        key={p.slug}
                        className={cn(
                          'px-4 py-3',
                          !row.all_same && row.values[p.slug] !== '—' && 'font-medium',
                        )}
                      >
                        {row.values[p.slug] || '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
