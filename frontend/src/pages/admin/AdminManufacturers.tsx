import { useState, useEffect } from 'react'
import { getAdminManufacturers, createManufacturer } from '@/services/hardwareApi'
import type { Manufacturer } from '@/types'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import LoadingState from '@/components/LoadingState'

export default function AdminManufacturers() {
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([])
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    getAdminManufacturers().then(setManufacturers).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await createManufacturer({ name })
      setName('')
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
      <h2 className="text-xl font-semibold mb-6">Manufacturers</h2>
      <form onSubmit={handleSubmit} className="flex gap-2 mb-6 max-w-md">
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Manufacturer name" required />
        <Button type="submit" disabled={saving}>Add</Button>
      </form>
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Slug</th>
            </tr>
          </thead>
          <tbody>
            {manufacturers.map((m, i) => (
              <tr key={m.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                <td className="px-4 py-3 font-medium">{m.name}</td>
                <td className="px-4 py-3 text-muted-foreground">{m.slug}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
