import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { Pagination as PaginationType } from '@/types'
import { Button } from './ui/button'

interface PaginationProps {
  pagination: PaginationType
  onPageChange: (page: number) => void
}

export default function Pagination({ pagination, onPageChange }: PaginationProps) {
  const { page, pages, total, has_prev, has_next } = pagination

  if (pages <= 1) return null

  return (
    <div className="flex items-center justify-between mt-8 pt-4 border-t border-border">
      <p className="text-sm text-muted-foreground">
        Page {page} of {pages} ({total} products)
      </p>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!has_prev}
          onClick={() => onPageChange(page - 1)}
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!has_next}
          onClick={() => onPageChange(page + 1)}
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
