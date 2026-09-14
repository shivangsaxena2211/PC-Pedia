import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Loader2 } from 'lucide-react'
import { searchProducts } from '@/services/hardwareApi'
import type { SearchResult } from '@/types'
import { Input } from './ui/input'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  onClose?: () => void
  autoFocus?: boolean
  className?: string
  placeholder?: string
}

export default function SearchBar({
  onClose,
  autoFocus = true,
  className,
  placeholder = 'Search hardware...',
}: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus()
  }, [autoFocus])

  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await searchProducts(query, 10)
        setResults(data)
        setShowResults(true)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowResults(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getResultUrl = (result: SearchResult) => {
    if (result.url_path) return result.url_path
    const cat = result.category_slug || 'cpu'
    const mfr = result.manufacturer_slug || 'unknown'
    return `/${cat}/${mfr}/${result.slug}`
  }

  const handleSelect = (result: SearchResult) => {
    navigate(getResultUrl(result))
    setQuery('')
    setShowResults(false)
    onClose?.()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (results.length > 0) {
      handleSelect(results[0])
    }
  }

  return (
    <div ref={containerRef} className={cn('relative w-full max-w-2xl mx-auto', className)}>
      <form onSubmit={handleSubmit} className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setShowResults(true)}
          placeholder={placeholder}
          className="pl-10 pr-10"
          aria-label="Search hardware"
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        )}
      </form>

      {showResults && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-lg border border-border bg-card shadow-lg z-50 overflow-hidden">
          {results.map((result) => (
            <button
              key={result.id}
              onClick={() => handleSelect(result)}
              className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-secondary transition-colors border-b border-border last:border-0"
            >
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{result.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {[result.category, result.family, result.generation, result.architecture]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              </div>
              <span className="text-xs text-primary font-medium shrink-0">
                {result.category}
              </span>
            </button>
          ))}
        </div>
      )}

      {showResults && query.length >= 2 && !loading && results.length === 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground text-center z-50">
          No results found for &ldquo;{query}&rdquo;
        </div>
      )}
    </div>
  )
}
