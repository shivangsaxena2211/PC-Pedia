import { useState, useEffect } from 'react'
import { getProductByPath } from '@/services/hardwareApi'
import type { Product } from '@/types'

export function useProduct(category: string, manufacturer: string, slug: string) {
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!category || !manufacturer || !slug) return
    setLoading(true)
    setError(null)
    getProductByPath(category, manufacturer, slug)
      .then(setProduct)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [category, manufacturer, slug])

  return { product, loading, error }
}
