import { Link } from 'react-router-dom'
import type { Product } from '@/types'
import { Card, CardContent } from './ui/card'
import { Badge } from './ui/badge'
import HardwareImage from './HardwareImage'
import { getProductUrl } from '@/lib/utils'

interface ProductCardProps {
  product: Product
  onCompare?: (product: Product) => void
}

function getHighlightSpecs(product: Product): { key: string; value: string }[] {
  const specs = product.quick_specs ?? {}
  const priority = [
    'VRAM', 'Total Cores', 'Threads', 'Capacity', 'Wattage',
    'Socket', 'TDP', 'Base Clock', 'Maximum Boost Clock', 'Frequency',
  ]
  const highlights: { key: string; value: string }[] = []

  for (const key of priority) {
    if (specs[key]) highlights.push({ key, value: specs[key] })
    if (highlights.length >= 4) break
  }

  if (highlights.length < 2) {
    for (const [key, value] of Object.entries(specs)) {
      if (!highlights.find((h) => h.key === key)) {
        highlights.push({ key, value })
        if (highlights.length >= 4) break
      }
    }
  }

  return highlights.slice(0, 4)
}

export default function ProductCard({ product, onCompare }: ProductCardProps) {
  const productUrl = getProductUrl(product)
  const highlights = getHighlightSpecs(product)

  return (
    <Card className="hardware-card group flex h-full flex-col hover:border-primary/50 transition-all duration-200 hover:shadow-md hover:shadow-primary/5 overflow-hidden">
      <Link to={productUrl} className="block shrink-0">
        <HardwareImage
          product={product}
          variant="card"
          className="hardware-card-image rounded-none border-0 border-b border-border/50 bg-gradient-to-b from-muted/30 to-transparent min-h-[11rem]"
        />
      </Link>

      <CardContent className="hardware-card-body flex flex-1 flex-col p-5">
        <div className="hardware-card-header pb-4">
          <div className="flex items-start justify-between gap-2 mb-1.5">
            <Badge variant="secondary" className="text-xs">
              {product.category}
            </Badge>
            {product.is_popular && (
              <Badge variant="default" className="text-xs">Popular</Badge>
            )}
          </div>

          {product.manufacturer && (
            <p className="text-xs text-primary font-medium mb-1">{product.manufacturer}</p>
          )}

          <Link to={productUrl}>
            <h3 className="font-semibold text-sm leading-[1.3] group-hover:text-primary transition-colors mb-1.5">
              {product.name}
            </h3>
          </Link>

          {(product.series || product.generation) && (
            <p className="text-xs text-muted-foreground leading-relaxed">
              {[product.series, product.generation].filter(Boolean).join(' · ')}
            </p>
          )}
        </div>

        {highlights.length > 0 && (
          <div className="hardware-card-specs flex flex-col gap-1.5">
            {highlights.map(({ key, value }) => (
              <div key={key} className="hardware-card-spec-row flex items-center justify-between gap-4 min-h-[30px] py-0.5 text-xs">
                <span className="hardware-card-spec-label flex-1 min-w-0 text-muted-foreground leading-snug">
                  {key}
                </span>
                <span className="hardware-card-spec-value flex-[0_1_auto] font-medium text-right leading-snug max-w-[60%] break-words">
                  {value}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="hardware-card-actions mt-4 flex items-center gap-2 pt-0.5">
          <Link
            to={productUrl}
            className="inline-flex h-10 flex-1 items-center justify-center rounded-md bg-secondary px-3.5 text-xs font-medium transition-colors hover:bg-secondary/80"
          >
            View Details
          </Link>
          {onCompare && (
            <button
              type="button"
              onClick={() => onCompare(product)}
              className="inline-flex h-10 shrink-0 items-center justify-center rounded-md border border-border px-3.5 text-xs font-medium transition-colors hover:bg-secondary"
            >
              Compare
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
