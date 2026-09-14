import { Skeleton } from './ui/skeleton'

interface LoadingStateProps {
  count?: number
}

export default function LoadingState({ count = 8 }: LoadingStateProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-lg border border-border p-4 space-y-3">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
          <Skeleton className="h-3 w-2/3" />
          <Skeleton className="h-8 w-full mt-4" />
        </div>
      ))}
    </div>
  )
}
