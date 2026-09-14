import { PackageOpen } from 'lucide-react'

interface EmptyStateProps {
  message?: string
}

export default function EmptyState({
  message = 'No products found matching your criteria.',
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <PackageOpen className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">No Results</h3>
      <p className="text-muted-foreground text-sm max-w-md">{message}</p>
    </div>
  )
}
