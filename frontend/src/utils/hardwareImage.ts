import type { Product } from '@/types'

/** Maps category slugs to local generic hardware illustration paths. */
const CATEGORY_FALLBACK_IMAGES: Record<string, string> = {
  cpu: '/images/hardware/cpu.svg',
  gpu: '/images/hardware/gpu.svg',
  ram: '/images/hardware/ram.svg',
  motherboards: '/images/hardware/motherboard.svg',
  motherboard: '/images/hardware/motherboard.svg',
  ssd: '/images/hardware/ssd.svg',
  psu: '/images/hardware/psu.svg',
  coolers: '/images/hardware/cooler.svg',
  cooler: '/images/hardware/cooler.svg',
  aio: '/images/hardware/aio.svg',
  fans: '/images/hardware/fan.svg',
  fan: '/images/hardware/fan.svg',
  cases: '/images/hardware/case.svg',
  case: '/images/hardware/case.svg',
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

export function getCategoryFallbackImage(categorySlug?: string | null): string {
  if (!categorySlug) return '/images/hardware/cpu.svg'
  const normalized = categorySlug.toLowerCase()
  return CATEGORY_FALLBACK_IMAGES[normalized] ?? '/images/hardware/cpu.svg'
}

/** Resolve product-specific image URL if one exists and is non-empty. */
export function getProductImageUrl(product?: Product | null): string | null {
  if (!product) return null

  const primary = product.primary_image_url?.trim()
  if (primary) return primary

  const legacy = product.image_url?.trim()
  if (legacy) return legacy

  const primaryImg = product.images?.find((img) => img.is_primary && img.url?.trim())
  if (primaryImg?.url) return primaryImg.url.trim()

  const firstImg = product.images?.find((img) => img.url?.trim())
  if (firstImg?.url) return firstImg.url.trim()

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

export function getImageVariantClasses(variant: ImageVariant): string {
  return `${VARIANT_ASPECT[variant]} ${VARIANT_PADDING[variant]}`
}

export function isLocalFallbackImage(src: string): boolean {
  return src.startsWith('/images/hardware/')
}
