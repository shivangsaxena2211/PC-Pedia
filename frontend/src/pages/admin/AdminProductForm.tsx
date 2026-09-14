import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  createProduct,
  getAdminCategories,
  getAdminManufacturers,
  getAdminSeries,
  getAdminGenerations,
} from '@/services/hardwareApi'
import type { Category, Manufacturer, Series, Generation } from '@/types'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'

export default function AdminProductForm() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Category[]>([])
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([])
  const [seriesList, setSeriesList] = useState<Series[]>([])
  const [generations, setGenerations] = useState<Generation[]>([])
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    name: '',
    manufacturer_id: '',
    category_id: '',
    series_id: '',
    generation_id: '',
    architecture: '',
    description: '',
    release_date: '',
    is_popular: false,
  })

  useEffect(() => {
    Promise.all([
      getAdminCategories(),
      getAdminManufacturers(),
      getAdminSeries(),
      getAdminGenerations(),
    ]).then(([cats, mfrs, series, gens]) => {
      setCategories(cats)
      setManufacturers(mfrs)
      setSeriesList(series)
      setGenerations(gens)
    })
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await createProduct({
        name: form.name,
        manufacturer_id: parseInt(form.manufacturer_id),
        category_id: parseInt(form.category_id),
        series_id: form.series_id ? parseInt(form.series_id) : undefined,
        generation_id: form.generation_id ? parseInt(form.generation_id) : undefined,
        architecture: form.architecture || undefined,
        description: form.description || undefined,
        release_date: form.release_date || undefined,
        is_popular: form.is_popular,
      })
      navigate('/admin/products')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create product')
    } finally {
      setSaving(false)
    }
  }

  const update = (key: string, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Add New Product</h2>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Product Name *</label>
          <Input value={form.name} onChange={(e) => update('name', e.target.value)} required />
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Category *</label>
          <Select value={form.category_id} onChange={(e) => update('category_id', e.target.value)} required>
            <option value="">Select category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </Select>
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Manufacturer *</label>
          <Select value={form.manufacturer_id} onChange={(e) => update('manufacturer_id', e.target.value)} required>
            <option value="">Select manufacturer</option>
            {manufacturers.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
          </Select>
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Series</label>
          <Select value={form.series_id} onChange={(e) => update('series_id', e.target.value)}>
            <option value="">Select series</option>
            {seriesList.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Generation</label>
          <Select value={form.generation_id} onChange={(e) => update('generation_id', e.target.value)}>
            <option value="">Select generation</option>
            {generations.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
          </Select>
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Architecture</label>
          <Input value={form.architecture} onChange={(e) => update('architecture', e.target.value)} />
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Release Date</label>
          <Input type="date" value={form.release_date} onChange={(e) => update('release_date', e.target.value)} />
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Description</label>
          <Input value={form.description} onChange={(e) => update('description', e.target.value)} />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="popular"
            checked={form.is_popular}
            onChange={(e) => update('is_popular', e.target.checked)}
          />
          <label htmlFor="popular" className="text-sm">Mark as popular</label>
        </div>
        <div className="flex gap-2 pt-4">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Create Product'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/products')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
