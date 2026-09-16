import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Loader2 } from 'lucide-react'
import { searchProducts } from '@/services/hardwareApi'
import type { SearchResult } from '@/types'

interface LandingSearchProps {
  variant?: 'navbar' | 'band'
  placeholder?: string
  showKbd?: boolean
  mobileShow?: boolean
  className?: string
  onCloseMobile?: () => void
}

export default function LandingSearch({
  variant = 'navbar',
  placeholder = 'Search CPUs, GPUs, motherboards...',
  showKbd = false,
  mobileShow = false,
  className = '',
  onCloseMobile,
}: LandingSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!showKbd) return
    const handleKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName
      if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA') {
        e.preventDefault()
        inputRef.current?.focus()
      }
      if (e.key === 'Escape') {
        setShowResults(false)
        onCloseMobile?.()
        inputRef.current?.blur()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [showKbd, onCloseMobile])

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
    onCloseMobile?.()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (results.length > 0) handleSelect(results[0])
  }

  const wrapClass =
    variant === 'navbar'
      ? `navbar-search${mobileShow ? ' mobile-show' : ''} ${className}`.trim()
      : `search-big ${className}`.trim()

  return (
    <div ref={containerRef} className={wrapClass}>
      <form onSubmit={handleSubmit} className="relative">
        <Search aria-hidden="true" />
        <input
          ref={inputRef}
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setShowResults(true)}
          placeholder={placeholder}
          aria-label="Search hardware"
          autoComplete="off"
        />
        {showKbd && <span className="search-kbd" aria-hidden="true">/</span>}
        {loading && (
          <Loader2
            className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground"
            style={{ color: 'var(--muted)' }}
            aria-hidden="true"
          />
        )}
      </form>

      {showResults && results.length > 0 && (
        <div className="landing-search-results">
          {results.map((result) => (
            <button
              key={result.id}
              type="button"
              onClick={() => handleSelect(result)}
              className="landing-search-result"
            >
              <div>
                <p>{result.name}</p>
                <p>
                  {[result.category, result.family, result.generation, result.architecture]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              </div>
              <span>{result.category}</span>
            </button>
          ))}
        </div>
      )}

      {showResults && query.length >= 2 && !loading && results.length === 0 && (
        <div className="landing-search-empty">
          No results found for &ldquo;{query}&rdquo;
        </div>
      )}
    </div>
  )
}
