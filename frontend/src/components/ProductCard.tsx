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
    <Card className="group hover:border-primary/50 transition-all duration-200 hover:shadow-md hover:shadow-primary/5 overflow-hidden">
      <Link to={productUrl} className="block">
        <HardwareImage
          product={product}
          variant="card"
          className="rounded-none border-0 border-b border-border/50 bg-gradient-to-b from-muted/30 to-transparent"
        />
      </Link>

      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <Badge variant="secondary" className="text-xs">
            {product.category}
          </Badge>
          {product.is_popular && (
            <Badge variant="default" className="text-xs">Popular</Badge>
          )}
        </div>

        {product.manufacturer && (
          <p className="text-xs text-primary font-medium mb-0.5">{product.manufacturer}</p>
        )}

        <Link to={productUrl}>
          <h3 className="font-semibold text-sm leading-tight group-hover:text-primary transition-colors line-clamp-2 mb-1">
            {product.name}
          </h3>
        </Link>

        {(product.series || product.generation) && (
          <p className="text-xs text-muted-foreground mb-3">
            {[product.series, product.generation].filter(Boolean).join(' · ')}
          </p>
        )}

        {highlights.length > 0 && (
          <div className="space-y-1 mb-4">
            {highlights.map(({ key, value }) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-muted-foreground">{key}</span>
                <span className="font-medium">{value}</span>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <Link
            to={productUrl}
            className="flex-1 text-center text-xs font-medium py-2 rounded-md bg-secondary hover:bg-secondary/80 transition-colors"
          >
            View Details
          </Link>
          {onCompare && (
            <button
              onClick={() => onCompare(product)}
              className="text-xs font-medium py-2 px-3 rounded-md border border-border hover:bg-secondary transition-colors"
            >
              Compare
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
