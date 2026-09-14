import { useState } from 'react'
import type { Product } from '@/types'
import {
  resolveHardwareImage,
  getCategoryFallbackImage,
  getHardwareImageAlt,
  getImageVariantClasses,
  type ImageVariant,
} from '@/utils/hardwareImage'
import { cn } from '@/lib/utils'

interface HardwareImageProps {
  product?: Product | null
  category?: string | null
  alt?: string
  className?: string
  variant?: ImageVariant
  imgClassName?: string
}

export default function HardwareImage({
  product,
  category,
  alt,
  className,
  variant = 'card',
  imgClassName,
}: HardwareImageProps) {
  const categorySlug = category ?? product?.category_slug ?? null
  const fallback = getCategoryFallbackImage(categorySlug)
  const resolvedSrc = resolveHardwareImage(product, categorySlug)

  const [failedSrc, setFailedSrc] = useState<string | null>(null)
  const src = failedSrc === resolvedSrc ? fallback : resolvedSrc
  const usingFallback = src === fallback

  const handleError = () => {
    if (!usingFallback) {
      setFailedSrc(resolvedSrc)
    }
  }

  const label = getHardwareImageAlt(product, categorySlug, alt)

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-lg bg-muted/40 border border-border/50 flex items-center justify-center',
        getImageVariantClasses(variant),
        className,
      )}
    >
      <img
        src={src}
        alt={label}
        onError={handleError}
        className={cn(
          'max-h-full max-w-full object-contain',
          usingFallback && 'opacity-90',
          imgClassName,
        )}
        loading="lazy"
        decoding="async"
      />
    </div>
  )
}
