import { useState, useEffect } from 'react'
import { getAdminGenerations, createGeneration, getAdminSeries } from '@/services/hardwareApi'
import type { Generation, Series } from '@/types'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import LoadingState from '@/components/LoadingState'

export default function AdminGenerations() {
  const [generations, setGenerations] = useState<Generation[]>([])
  const [seriesList, setSeriesList] = useState<Series[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', series_id: '', architecture: '', release_year: '' })
  const [saving, setSaving] = useState(false)

  const load = () => {
    Promise.all([getAdminGenerations(), getAdminSeries()])
      .then(([g, s]) => { setGenerations(g); setSeriesList(s) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await createGeneration({
        name: form.name,
        series_id: parseInt(form.series_id),
        architecture: form.architecture || undefined,
        release_year: form.release_year ? parseInt(form.release_year) : undefined,
      })
      setForm({ name: '', series_id: '', architecture: '', release_year: '' })
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
      <h2 className="text-xl font-semibold mb-6">Generations</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-5 gap-2 mb-6">
        <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Generation name" required />
        <Select value={form.series_id} onChange={(e) => setForm({ ...form, series_id: e.target.value })} required>
          <option value="">Series</option>
          {seriesList.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </Select>
        <Input value={form.architecture} onChange={(e) => setForm({ ...form, architecture: e.target.value })} placeholder="Architecture" />
        <Input value={form.release_year} onChange={(e) => setForm({ ...form, release_year: e.target.value })} placeholder="Year" type="number" />
        <Button type="submit" disabled={saving}>Add</Button>
      </form>
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Series</th>
              <th className="px-4 py-3 text-left">Architecture</th>
            </tr>
          </thead>
          <tbody>
            {generations.map((g, i) => (
              <tr key={g.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                <td className="px-4 py-3 font-medium">{g.name}</td>
                <td className="px-4 py-3 text-muted-foreground">{g.series}</td>
                <td className="px-4 py-3 text-muted-foreground">{g.architecture || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
