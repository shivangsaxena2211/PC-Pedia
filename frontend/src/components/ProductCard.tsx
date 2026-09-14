import { Link } from 'react-router-dom'
import { Calendar, Building2 } from 'lucide-react'
import type { Product } from '@/types'
import { Card, CardContent } from './ui/card'
import { Badge } from './ui/badge'
import { formatDate, getProductUrl } from '@/lib/utils'

interface ProductCardProps {
  product: Product
  onCompare?: (product: Product) => void
}

export default function ProductCard({ product, onCompare }: ProductCardProps) {
  const productUrl = getProductUrl(product)

  return (
    <Card className="group hover:border-primary/50 transition-all duration-200 hover:shadow-md hover:shadow-primary/5">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2 mb-3">
          <Badge variant="secondary" className="text-xs">
            {product.category}
          </Badge>
          {product.is_popular && (
            <Badge variant="default" className="text-xs">Popular</Badge>
          )}
        </div>

        <Link to={productUrl}>
          <h3 className="font-semibold text-sm leading-tight group-hover:text-primary transition-colors line-clamp-2 mb-2">
            {product.name}
          </h3>
        </Link>

        <div className="space-y-1.5 text-xs text-muted-foreground">
          {product.manufacturer && (
            <div className="flex items-center gap-1.5">
              <Building2 className="h-3 w-3" />
              <span>{product.manufacturer}</span>
            </div>
          )}
          {product.family && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted-foreground/60">Family:</span>
              <span>{product.family}</span>
            </div>
          )}
          {product.generation && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted-foreground/60">Gen:</span>
              <span>{product.generation}</span>
            </div>
          )}
          {product.release_date && (
            <div className="flex items-center gap-1.5">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(product.release_date)}</span>
            </div>
          )}
        </div>

        {product.quick_specs && Object.keys(product.quick_specs).length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {Object.entries(product.quick_specs).slice(0, 3).map(([key, val]) => (
              <span key={key} className="text-xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                {key}: {val}
              </span>
            ))}
          </div>
        )}

        <div className="flex gap-2 mt-4">
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
