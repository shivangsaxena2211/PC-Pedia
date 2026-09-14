import { useState, useEffect, useCallback } from 'react'
import { getProducts, getCategoryApiEndpoint, type ProductQueryParams } from '@/services/hardwareApi'
import type { ProductListResponse } from '@/types'

export function useProducts(categorySlug: string, params: ProductQueryParams) {
  const [data, setData] = useState<ProductListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const endpoint = getCategoryApiEndpoint(categorySlug)

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await getProducts(endpoint, params)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load products')
    } finally {
      setLoading(false)
    }
  }, [endpoint, JSON.stringify(params)])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  return { data, loading, error, refetch: fetchProducts }
}
