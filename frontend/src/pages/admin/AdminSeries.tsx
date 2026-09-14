import { useState, useEffect } from 'react'
import { getAdminSeries, createSeries, getAdminManufacturers, getAdminCategories } from '@/services/hardwareApi'
import type { Series, Manufacturer, Category } from '@/types'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import LoadingState from '@/components/LoadingState'

export default function AdminSeries() {
  const [seriesList, setSeriesList] = useState<Series[]>([])
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', manufacturer_id: '', category_id: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    Promise.all([getAdminSeries(), getAdminManufacturers(), getAdminCategories()])
      .then(([s, m, c]) => { setSeriesList(s); setManufacturers(m); setCategories(c) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await createSeries({
        name: form.name,
        manufacturer_id: parseInt(form.manufacturer_id),
        category_id: parseInt(form.category_id),
      })
      setForm({ name: '', manufacturer_id: '', category_id: '' })
      load()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingState count={3} />

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Series</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-2 mb-6">
        <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Series name" required />
        <Select value={form.manufacturer_id} onChange={(e) => setForm({ ...form, manufacturer_id: e.target.value })} required>
          <option value="">Manufacturer</option>
          {manufacturers.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
        </Select>
        <Select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
          <option value="">Category</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </Select>
        <Button type="submit" disabled={saving}>Add</Button>
      </form>
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Manufacturer</th>
              <th className="px-4 py-3 text-left">Slug</th>
            </tr>
          </thead>
          <tbody>
            {seriesList.map((s, i) => (
              <tr key={s.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                <td className="px-4 py-3 font-medium">{s.name}</td>
                <td className="px-4 py-3 text-muted-foreground">{s.manufacturer}</td>
                <td className="px-4 py-3 text-muted-foreground">{s.slug}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
