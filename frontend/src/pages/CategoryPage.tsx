import { useState, useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import { useCategories } from '@/hooks/useCategories'
import { useProducts } from '@/hooks/useProducts'
import { useCompare } from '@/hooks/useCompare'
import Breadcrumbs from '@/components/Breadcrumbs'
import FilterPanel, { type FilterState } from '@/components/FilterPanel'
import ProductCard from '@/components/ProductCard'
import Pagination from '@/components/Pagination'
import LoadingState from '@/components/LoadingState'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import { getCategoryIcon } from '@/utils/categories'
import type { ProductQueryParams } from '@/services/hardwareApi'

const DEFAULT_FILTERS: FilterState = {
  search: '',
  manufacturer: '',
  family: '',
  series: '',
  generation: '',
  sort: '-release_date',
  specFilters: {},
}

export default function CategoryPage() {
  const location = useLocation()
  const categorySlug = location.pathname.replace('/', '')
  const { categories } = useCategories()
  const category = categories.find((c) => c.slug === categorySlug)
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS)
  const [page, setPage] = useState(1)
  const { addToCompare } = useCompare()

  const queryParams = useMemo((): ProductQueryParams => {
    const params: ProductQueryParams = {
      page,
      limit: 24,
      search: filters.search || undefined,
      manufacturer: filters.manufacturer || undefined,
      family: filters.family || undefined,
      series: filters.series || undefined,
      generation: filters.generation || undefined,
      sort: filters.sort || undefined,
    }
    for (const [key, value] of Object.entries(filters.specFilters)) {
      if (value) params[`spec_${key}`] = value
    }
    return params
  }, [page, filters])

  const { data, loading, error, refetch } = useProducts(categorySlug, queryParams)

  if (!category && !loading) {
    return <ErrorState message="Category not found." />
  }

  const Icon = getCategoryIcon(category?.icon || categorySlug)

  const handleCompare = (product: Parameters<typeof addToCompare>[0]) => {
    try {
      addToCompare(product)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Cannot add to compare')
    }
  }

  const listKeySpecs = categorySlug === 'cpu'
    ? ['Cores', 'Threads', 'Base Clock', 'Socket', 'TDP']
    : categorySlug === 'gpu'
      ? ['VRAM', 'CUDA Cores', 'TDP', 'Memory Type']
      : []

  return (
    <div className="mx-auto max-w-7xl px-4 lg:px-8 py-8">
      <Breadcrumbs items={[{ label: category?.name || categorySlug }]} />

      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-lg bg-primary/10 text-primary">
          <Icon className="h-6 w-6" />
        </div>
        <h1 className="text-3xl font-bold">{category?.name || categorySlug}</h1>
      </div>
      <p className="text-muted-foreground mb-8">{category?.description}</p>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1">
          <FilterPanel
            filters={data?.filters}
            state={filters}
            onChange={(f) => { setFilters(f); setPage(1) }}
            onReset={() => { setFilters(DEFAULT_FILTERS); setPage(1) }}
          />
        </aside>

        <div className="lg:col-span-3">
          {loading && <LoadingState />}
          {error && <ErrorState message={error} onRetry={refetch} />}
          {!loading && !error && data?.data.length === 0 && <EmptyState />}
          {!loading && !error && data && data.data.length > 0 && (
            <>
              <p className="text-sm text-muted-foreground mb-4">
                {data.pagination.total} product{data.pagination.total !== 1 ? 's' : ''} found
              </p>

              {listKeySpecs.length > 0 && (
                <div className="hidden md:block rounded-lg border border-border overflow-hidden mb-4">
                  <table className="w-full text-sm">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">Product</th>
                        {listKeySpecs.map((k) => (
                          <th key={k} className="px-4 py-2 text-left font-medium">{k}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {data.data.map((product, i) => (
                        <tr key={product.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                          <td className="px-4 py-2 font-medium">{product.name}</td>
                          {listKeySpecs.map((k) => (
                            <td key={k} className="px-4 py-2 text-muted-foreground">
                              {product.quick_specs?.[k] ?? '—'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {data.data.map((product) => (
                  <ProductCard key={product.id} product={product} onCompare={handleCompare} />
                ))}
              </div>
              <Pagination
                pagination={data.pagination}
                onPageChange={setPage}
              />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
