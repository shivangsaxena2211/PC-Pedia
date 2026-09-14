import { Search } from 'lucide-react'
import type { FilterOptions, SpecificationDefinition } from '@/types'
import { Input } from './ui/input'
import { Select } from './ui/select'
import { Button } from './ui/button'

export interface FilterState {
  search: string
  manufacturer: string
  family: string
  series: string
  generation: string
  sort: string
  specFilters: Record<string, string>
}

interface FilterPanelProps {
  filters: FilterOptions | undefined
  state: FilterState
  onChange: (state: FilterState) => void
  onReset: () => void
}

export default function FilterPanel({ filters, state, onChange, onReset }: FilterPanelProps) {
  const update = (key: keyof Omit<FilterState, 'specFilters'>, value: string) => {
    onChange({ ...state, [key]: value })
  }

  const updateSpecFilter = (key: string, value: string) => {
    onChange({
      ...state,
      specFilters: { ...state.specFilters, [key]: value },
    })
  }

  const filterableSpecs: SpecificationDefinition[] =
    filters?.filterable_specifications ?? []

  return (
    <div className="space-y-4 p-4 rounded-lg border border-border bg-card">
      <h3 className="font-semibold text-sm">Filters</h3>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search products..."
          value={state.search}
          onChange={(e) => update('search', e.target.value)}
          className="pl-10"
        />
      </div>

      <div>
        <label className="text-xs text-muted-foreground mb-1.5 block">Manufacturer</label>
        <Select value={state.manufacturer} onChange={(e) => update('manufacturer', e.target.value)}>
          <option value="">All Manufacturers</option>
          {filters?.manufacturers.map((m) => (
            <option key={m.id} value={m.slug}>{m.name}</option>
          ))}
        </Select>
      </div>

      {filters?.families && filters.families.length > 0 && (
        <div>
          <label className="text-xs text-muted-foreground mb-1.5 block">Family</label>
          <Select value={state.family} onChange={(e) => update('family', e.target.value)}>
            <option value="">All Families</option>
            {filters.families.map((f) => (
              <option key={f.id} value={f.slug}>{f.name}</option>
            ))}
          </Select>
        </div>
      )}

      <div>
        <label className="text-xs text-muted-foreground mb-1.5 block">Series</label>
        <Select value={state.series} onChange={(e) => update('series', e.target.value)}>
          <option value="">All Series</option>
          {filters?.series.map((s) => (
            <option key={s.id} value={s.slug}>{s.name}</option>
          ))}
        </Select>
      </div>

      <div>
        <label className="text-xs text-muted-foreground mb-1.5 block">Generation</label>
        <Select value={state.generation} onChange={(e) => update('generation', e.target.value)}>
          <option value="">All Generations</option>
          {filters?.generations.map((g) => (
            <option key={g.id} value={g.slug}>{g.name}</option>
          ))}
        </Select>
      </div>

      {filterableSpecs.length > 0 && (
        <div className="border-t border-border pt-4 space-y-3">
          <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Specifications
          </h4>
          {filterableSpecs.map((spec) => (
            <div key={spec.key}>
              <label className="text-xs text-muted-foreground mb-1.5 block">
                {spec.display_name}
              </label>
              <Input
                placeholder={`Filter by ${spec.display_name}`}
                value={state.specFilters[spec.key] || ''}
                onChange={(e) => updateSpecFilter(spec.key, e.target.value)}
              />
            </div>
          ))}
        </div>
      )}

      <div>
        <label className="text-xs text-muted-foreground mb-1.5 block">Sort By</label>
        <Select value={state.sort} onChange={(e) => update('sort', e.target.value)}>
          <option value="-release_date">Release Date (Newest)</option>
          <option value="release_date">Release Date (Oldest)</option>
          <option value="name">Name (A-Z)</option>
          <option value="-name">Name (Z-A)</option>
          <option value="-created_at">Recently Added</option>
        </Select>
      </div>

      <Button variant="outline" size="sm" onClick={onReset} className="w-full">
        Reset Filters
      </Button>
    </div>
  )
}
