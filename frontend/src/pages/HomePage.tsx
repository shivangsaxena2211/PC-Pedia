import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { GitCompareArrows, ArrowRight } from 'lucide-react'
import { getHomeData } from '@/services/hardwareApi'
import { useCategories } from '@/hooks/useCategories'
import type { HomeData } from '@/types'
import { getCategoryIcon } from '@/utils/categories'
import SearchBar from '@/components/SearchBar'
import ProductCard from '@/components/ProductCard'
import LoadingState from '@/components/LoadingState'
import ErrorState from '@/components/ErrorState'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { getCategoryPath } from '@/lib/utils'

export default function HomePage() {
  const [data, setData] = useState<HomeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { categories } = useCategories()

  useEffect(() => {
    getHomeData()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />

  return (
    <div>
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 lg:px-8 py-20 lg:py-28 text-center">
          <h1 className="text-4xl lg:text-6xl font-bold tracking-tight mb-4">
            PC HARDWARE DATABASE
          </h1>
          <p className="text-xl lg:text-2xl text-muted-foreground mb-2">
            Explore. Compare. Understand.
          </p>
          <p className="text-muted-foreground mb-8">
            A comprehensive encyclopedia for computer hardware.
          </p>
          <SearchBar className="max-w-xl" placeholder="Search CPUs, GPUs, RAM, SSDs..." />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 lg:px-8 py-16">
        <h2 className="text-2xl font-bold mb-8">Browse Categories</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {categories.map((cat) => {
            const Icon = getCategoryIcon(cat.icon || cat.slug)
            return (
              <Link key={cat.slug} to={getCategoryPath(cat.slug)}>
                <Card className="group hover:border-primary/50 transition-all duration-200 h-full">
                  <CardContent className="p-6 flex flex-col items-center text-center gap-3">
                    <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
                      <Icon className="h-8 w-8" />
                    </div>
                    <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                      {cat.name}
                    </h3>
                    <p className="text-sm text-muted-foreground">{cat.description}</p>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 lg:px-8 py-16 border-t border-border">
        <h2 className="text-2xl font-bold mb-8">Popular Hardware</h2>
        {loading ? <LoadingState count={4} /> : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {data?.popular.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      <section className="mx-auto max-w-7xl px-4 lg:px-8 py-16 border-t border-border">
        <h2 className="text-2xl font-bold mb-8">Latest Hardware</h2>
        {loading ? <LoadingState count={4} /> : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {data?.latest.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      <section className="mx-auto max-w-7xl px-4 lg:px-8 py-16 border-t border-border">
        <h2 className="text-2xl font-bold mb-8">Manufacturers</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {data?.manufacturers.map((mfr) => (
            <div
              key={mfr.id}
              className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-card hover:border-primary/50 transition-colors"
            >
              {mfr.logo_url ? (
                <img
                  src={mfr.logo_url}
                  alt={mfr.name}
                  className="h-8 w-auto object-contain"
                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                />
              ) : (
                <div className="h-8 w-8 rounded bg-secondary flex items-center justify-center text-xs font-bold">
                  {mfr.name.charAt(0)}
                </div>
              )}
              <span className="text-sm font-medium text-center">{mfr.name}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 lg:px-8 py-16 border-t border-border">
        <div className="rounded-xl border border-border bg-card p-8 lg:p-12 flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <GitCompareArrows className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Compare Hardware</h2>
              <p className="text-muted-foreground mt-1">
                Side-by-side specification comparison for CPUs, GPUs, and more.
              </p>
            </div>
          </div>
          <Link to="/compare">
            <Button size="lg" className="gap-2">
              Start Comparing
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
