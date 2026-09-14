import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { Product } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function getProductUrl(product: Product): string {
  if (product.url_path) return product.url_path
  const cat = product.category_slug || 'cpu'
  const mfr = product.manufacturer_slug || 'unknown'
  return `/${cat}/${mfr}/${product.slug}`
}

export function getCategoryPath(slug: string): string {
  return `/${slug}`
}
