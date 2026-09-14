import type { Product } from '@/types'

/** Canonical category keys used for fallback SVG assets. */
const CATEGORY_ASSET_KEYS: Record<string, string> = {
  cpu: 'cpu',
  cpus: 'cpu',
  gpu: 'gpu',
  gpus: 'gpu',
  ram: 'ram',
  motherboard: 'motherboard',
  motherboards: 'motherboard',
  ssd: 'ssd',
  ssds: 'ssd',
  psu: 'psu',
  psus: 'psu',
  cooler: 'cooler',
  coolers: 'cooler',
  aio: 'aio',
  aios: 'aio',
  fan: 'fan',
  fans: 'fan',
  case: 'case',
  cases: 'case',
}

const CATEGORY_FALLBACK_IMAGES: Record<string, string> = {
  cpu: '/images/hardware/cpu.svg',
  gpu: '/images/hardware/gpu.svg',
  ram: '/images/hardware/ram.svg',
  motherboard: '/images/hardware/motherboard.svg',
  ssd: '/images/hardware/ssd.svg',
  psu: '/images/hardware/psu.svg',
  cooler: '/images/hardware/cooler.svg',
  aio: '/images/hardware/aio.svg',
  fan: '/images/hardware/fan.svg',
  case: '/images/hardware/case.svg',
}

const CATEGORY_ALT_LABELS: Record<string, string> = {
  cpu: 'CPU hardware illustration',
  gpu: 'GPU hardware illustration',
  ram: 'RAM hardware illustration',
  motherboard: 'Motherboard hardware illustration',
  ssd: 'SSD hardware illustration',
  psu: 'PSU hardware illustration',
  cooler: 'CPU cooler hardware illustration',
  aio: 'AIO liquid cooler hardware illustration',
  fan: 'PC case fan hardware illustration',
  case: 'PC case hardware illustration',
}

export type ImageVariant = 'thumbnail' | 'card' | 'detail'

const VARIANT_ASPECT: Record<ImageVariant, string> = {
  thumbnail: 'aspect-square',
  card: 'aspect-[4/3]',
  detail: 'aspect-[4/3]',
}

const VARIANT_PADDING: Record<ImageVariant, string> = {
  thumbnail: 'p-3',
  card: 'p-4',
  detail: 'p-8',
}

export function normalizeCategorySlug(categorySlug?: string | null): string {
  if (!categorySlug) return 'cpu'
  const normalized = categorySlug.toLowerCase()
  return CATEGORY_ASSET_KEYS[normalized] ?? normalized
}

export function getCategoryFallbackImage(categorySlug?: string | null): string {
  const key = normalizeCategorySlug(categorySlug)
  return CATEGORY_FALLBACK_IMAGES[key] ?? '/images/hardware/cpu.svg'
}

/**
 * Resolve product-specific image URL if one exists and is non-empty.
 *
 * Priority:
 *   1. API-resolved primary_image_url
 *   2. ProductImage marked primary
 *   3. First valid ProductImage
 *   4. Product.image_url
 */
export function getProductImageUrl(product?: Product | null): string | null {
  if (!product) return null

  const resolved = product.primary_image_url?.trim()
  if (resolved) return resolved

  const primaryImg = product.images?.find((img) => img.is_primary && img.url?.trim())
  if (primaryImg?.url) return primaryImg.url.trim()

  const firstImg = product.images?.find((img) => img.url?.trim())
  if (firstImg?.url) return firstImg.url.trim()

  const legacy = product.image_url?.trim()
  if (legacy) return legacy

  return null
}

/** Product image URL or category fallback — never returns empty. */
export function resolveHardwareImage(
  product?: Product | null,
  categorySlug?: string | null,
): string {
  const productUrl = getProductImageUrl(product)
  if (productUrl) return productUrl

  const slug = categorySlug ?? product?.category_slug ?? product?.category?.toLowerCase()
  return getCategoryFallbackImage(slug)
}

export function getHardwareImageAlt(
  product?: Product | null,
  categorySlug?: string | null,
  explicitAlt?: string,
): string {
  if (explicitAlt?.trim()) return explicitAlt.trim()

  const productUrl = getProductImageUrl(product)
  if (product?.name && productUrl) return product.name

  const key = normalizeCategorySlug(categorySlug ?? product?.category_slug)
  return CATEGORY_ALT_LABELS[key] ?? 'Hardware illustration'
}

export function getImageVariantClasses(variant: ImageVariant): string {
  return `${VARIANT_ASPECT[variant]} ${VARIANT_PADDING[variant]}`
}

export function isLocalFallbackImage(src: string): boolean {
  return src.startsWith('/images/hardware/')
}
