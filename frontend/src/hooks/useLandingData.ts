import { useEffect, useState } from 'react'
import { getCategories, getGenerations, getHomeData } from '@/services/hardwareApi'
import type { Category, Generation, HomeData } from '@/types'

export interface LandingData {
  home: HomeData | null
  categories: Category[]
  intelGenerations: Generation[]
  amdGenerations: Generation[]
}

export function useLandingData() {
  const [data, setData] = useState<LandingData>({
    home: null,
    categories: [],
    intelGenerations: [],
    amdGenerations: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [home, categories, generations] = await Promise.all([
          getHomeData(),
          getCategories(true),
          getGenerations('cpu'),
        ])

        if (cancelled) return

        const intelGenerations = generations.filter((gen) => {
          const series = (gen.series ?? '').toLowerCase()
          const name = gen.name.toLowerCase()
          return series.includes('core') || name.includes('generation')
        })

        const amdGenerations = generations.filter((gen) => {
          const series = (gen.series ?? '').toLowerCase()
          const name = gen.name.toLowerCase()
          return series.includes('ryzen') || name.includes('ryzen')
        })

        setData({
          home,
          categories,
          intelGenerations,
          amdGenerations,
        })
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load landing data')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const hasCounts = !loading && !error && data.categories.some((cat) => cat.product_count != null)

  const totalProducts = hasCounts
    ? data.categories.reduce((sum, cat) => sum + (cat.product_count ?? 0), 0)
    : null

  const countForSlug = (slug: string): number | null => {
    if (!hasCounts) return null
    const category = data.categories.find((cat) => cat.slug === slug)
    if (!category || category.product_count == null) return null
    return category.product_count
  }

  return {
    ...data,
    loading,
    error,
    statsReady: hasCounts,
    totalProducts,
    cpuCount: countForSlug('cpu'),
    gpuCount: countForSlug('gpu'),
    motherboardCount: countForSlug('motherboards'),
    categoryCount: data.categories.length,
  }
}
