import { useState, useCallback } from 'react'
import type { Product } from '@/types'

const STORAGE_KEY = 'pc-hardware-compare'

export function useCompare() {
  const [compareList, setCompareList] = useState<Product[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })

  const save = useCallback((list: Product[]) => {
    setCompareList(list)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
  }, [])

  const addToCompare = useCallback((product: Product) => {
    if (compareList.some((p) => p.slug === product.slug)) return
    if (compareList.length > 0 && compareList[0].category_slug !== product.category_slug) {
      throw new Error('Can only compare products from the same category')
    }
    if (compareList.length >= 4) {
      throw new Error('Maximum 4 products can be compared')
    }
    save([...compareList, product])
  }, [compareList, save])

  const removeFromCompare = useCallback((slug: string) => {
    save(compareList.filter((p) => p.slug !== slug))
  }, [compareList, save])

  const clearCompare = useCallback(() => {
    save([])
  }, [save])

  return { compareList, addToCompare, removeFromCompare, clearCompare }
}
