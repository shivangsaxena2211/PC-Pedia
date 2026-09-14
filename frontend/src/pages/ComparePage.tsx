import { useState, useEffect } from 'react'
import { X, GitCompareArrows } from 'lucide-react'
import { useCompare } from '@/hooks/useCompare'
import { compareProducts } from '@/services/hardwareApi'
import type { ComparisonResponse } from '@/types'
import ComparisonTable from '@/components/ComparisonTable'
import SearchBar from '@/components/SearchBar'
import ErrorState from '@/components/ErrorState'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function ComparePage() {
  const { compareList, removeFromCompare, clearCompare } = useCompare()
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (compareList.length < 2) {
      setComparison(null)
      return
    }

    setLoading(true)
    setError(null)
    compareProducts(compareList.map((p) => p.slug))
      .then(setComparison)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [compareList])

  return (
    <div className="mx-auto max-w-7xl px-4 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-2">
        <GitCompareArrows className="h-8 w-8 text-primary" />
        <h1 className="text-3xl font-bold">Compare Hardware</h1>
      </div>
      <p className="text-muted-foreground mb-8">
        Select products from the same category to compare specifications side-by-side.
      </p>

      {/* Selected products */}
      <div className="flex flex-wrap gap-3 mb-6">
        {compareList.map((product) => (
          <div
            key={product.slug}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-card"
          >
            <Badge variant="secondary" className="text-xs">{product.category}</Badge>
            <span className="text-sm font-medium">{product.name}</span>
            <button
              onClick={() => removeFromCompare(product.slug)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
        {compareList.length > 0 && (
          <Button variant="outline" size="sm" onClick={clearCompare}>Clear All</Button>
        )}
      </div>

      {compareList.length < 2 && (
        <div className="mb-8">
          <p className="text-sm text-muted-foreground mb-4">
            Search and select at least 2 products to compare (max 4, same category only).
          </p>
          <SearchBar placeholder="Search products to compare..." />
        </div>
      )}

      {loading && (
        <div className="text-center py-12 text-muted-foreground">Loading comparison...</div>
      )}

      {error && <ErrorState message={error} />}

      {comparison && !loading && !error && (
        <ComparisonTable data={comparison} />
      )}
    </div>
  )
}
