import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAdminProducts } from '@/services/hardwareApi'
import type { Product } from '@/types'
import LoadingState from '@/components/LoadingState'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function AdminProducts() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAdminProducts()
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState />

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Products ({products?.length ?? 0})</h2>
        <Link to="/admin/products/new">
          <Button size="sm">Add Product</Button>
        </Link>
      </div>
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Name</th>
              <th className="px-4 py-3 text-left font-medium">Category</th>
              <th className="px-4 py-3 text-left font-medium">Manufacturer</th>
              <th className="px-4 py-3 text-left font-medium">Popular</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p, i) => (
              <tr key={p.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                <td className="px-4 py-3 font-medium">{p.name}</td>
                <td className="px-4 py-3"><Badge variant="secondary">{p.category}</Badge></td>
                <td className="px-4 py-3 text-muted-foreground">{p.manufacturer}</td>
                <td className="px-4 py-3">{p.is_popular ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
