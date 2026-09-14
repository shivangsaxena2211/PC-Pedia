import { useEffect, useState } from 'react'
import { getAdminDashboard } from '@/services/hardwareApi'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import LoadingState from '@/components/LoadingState'

export default function AdminDashboard() {
  const [stats, setStats] = useState<Record<string, number> | null>(null)

  useEffect(() => {
    getAdminDashboard().then(setStats)
  }, [])

  if (!stats) return <LoadingState count={3} />

  const items = [
    { label: 'Products', value: stats.products },
    { label: 'Categories', value: stats.categories },
    { label: 'Manufacturers', value: stats.manufacturers },
    { label: 'Series', value: stats.series },
    { label: 'Generations', value: stats.generations },
  ]

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {items.map((item) => (
          <Card key={item.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">{item.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{item.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <p className="text-sm text-muted-foreground mt-6">
        Authentication is not yet implemented. This admin panel is ready for future auth integration.
      </p>
    </div>
  )
}
