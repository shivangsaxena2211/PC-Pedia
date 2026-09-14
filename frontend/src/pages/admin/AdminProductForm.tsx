import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  createProduct,
  getAdminCategories,
  getAdminManufacturers,
  getAdminSeries,
  getAdminGenerations,
} from '@/services/hardwareApi'
import type { Category, Manufacturer, Series, Generation, ProductImageInput } from '@/types'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import HardwareImage from '@/components/HardwareImage'
import { getCategoryFallbackImage } from '@/utils/hardwareImage'

const IMAGE_TYPES = ['primary', 'front', 'back', 'side', 'installed', 'diagram', 'thumbnail']

interface ImageRow extends ProductImageInput {
  _previewError?: boolean
}

export default function AdminProductForm() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Category[]>([])
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([])
  const [seriesList, setSeriesList] = useState<Series[]>([])
  const [generations, setGenerations] = useState<Generation[]>([])
  const [saving, setSaving] = useState(false)
  const [primaryPreviewError, setPrimaryPreviewError] = useState(false)

  const [form, setForm] = useState({
    name: '',
    manufacturer_id: '',
    category_id: '',
    series_id: '',
    generation_id: '',
    architecture: '',
    description: '',
    release_date: '',
    image_url: '',
    is_popular: false,
  })

  const [additionalImages, setAdditionalImages] = useState<ImageRow[]>([])

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

  const selectedCategory = categories.find((c) => c.id === parseInt(form.category_id))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      const images: ProductImageInput[] = additionalImages
        .filter((img) => img.url.trim())
        .map((img, i) => ({
          url: img.url.trim(),
          alt_text: img.alt_text || form.name,
          image_type: img.image_type || 'primary',
          is_primary: img.is_primary ?? false,
          sort_order: img.sort_order ?? i + 1,
        }))

      await createProduct({
        name: form.name,
        manufacturer_id: parseInt(form.manufacturer_id),
        category_id: parseInt(form.category_id),
        series_id: form.series_id ? parseInt(form.series_id) : undefined,
        generation_id: form.generation_id ? parseInt(form.generation_id) : undefined,
        architecture: form.architecture || undefined,
        description: form.description || undefined,
        release_date: form.release_date || undefined,
        image_url: form.image_url.trim() || undefined,
        is_popular: form.is_popular,
        images: images.length > 0 ? images : undefined,
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
    if (key === 'image_url') setPrimaryPreviewError(false)
  }

  const addImageRow = () => {
    setAdditionalImages((prev) => [
      ...prev,
      { url: '', alt_text: '', image_type: 'primary', is_primary: false, sort_order: prev.length + 1 },
    ])
  }

  const updateImageRow = (index: number, field: keyof ImageRow, value: string | boolean) => {
    setAdditionalImages((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value, _previewError: false } : row)),
    )
  }

  const removeImageRow = (index: number) => {
    setAdditionalImages((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Add New Product</h2>
      <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </div>

        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Description</label>
          <Input value={form.description} onChange={(e) => update('description', e.target.value)} />
        </div>

        <div className="border-t border-border pt-6 space-y-4">
          <h3 className="font-semibold">Product Images</h3>

          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Primary Image URL</label>
            <Input
              value={form.image_url}
              onChange={(e) => update('image_url', e.target.value)}
              placeholder="https://example.com/product-image.jpg"
            />
            <div className="mt-3 max-w-xs">
              {form.image_url && !primaryPreviewError ? (
                <img
                  src={form.image_url}
                  alt="Primary preview"
                  className="w-full aspect-[4/3] object-contain rounded-lg border border-border bg-muted/30 p-2"
                  onError={() => setPrimaryPreviewError(true)}
                />
              ) : form.image_url && primaryPreviewError ? (
                <p className="text-sm text-amber-500">Could not load image from URL. Check the link.</p>
              ) : (
                <HardwareImage
                  category={selectedCategory?.slug}
                  alt="Category fallback preview"
                  variant="card"
                />
              )}
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Additional Images</label>
              <Button type="button" variant="outline" size="sm" onClick={addImageRow}>
                Add Image
              </Button>
            </div>

            {additionalImages.map((img, index) => (
              <div key={index} className="p-4 rounded-lg border border-border space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Image URL</label>
                    <Input
                      value={img.url}
                      onChange={(e) => updateImageRow(index, 'url', e.target.value)}
                      placeholder="https://..."
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Alt Text</label>
                    <Input
                      value={img.alt_text || ''}
                      onChange={(e) => updateImageRow(index, 'alt_text', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Image Type</label>
                    <Select
                      value={img.image_type || 'primary'}
                      onChange={(e) => updateImageRow(index, 'image_type', e.target.value)}
                    >
                      {IMAGE_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground mb-1 block">Display Order</label>
                    <Input
                      type="number"
                      value={img.sort_order ?? index + 1}
                      onChange={(e) => updateImageRow(index, 'sort_order', e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`primary-${index}`}
                    checked={img.is_primary ?? false}
                    onChange={(e) => updateImageRow(index, 'is_primary', e.target.checked)}
                  />
                  <label htmlFor={`primary-${index}`} className="text-xs">Mark as primary image</label>
                </div>
                {img.url && !img._previewError && (
                  <img
                    src={img.url}
                    alt={img.alt_text || 'Preview'}
                    className="h-24 object-contain rounded border border-border bg-muted/30 p-2"
                    onError={() => updateImageRow(index, '_previewError', true)}
                  />
                )}
                {img._previewError && (
                  <p className="text-xs text-amber-500">Image URL could not be loaded.</p>
                )}
                <Button type="button" variant="outline" size="sm" onClick={() => removeImageRow(index)}>
                  Remove
                </Button>
              </div>
            ))}
          </div>

          {!form.image_url && additionalImages.length === 0 && selectedCategory && (
            <p className="text-xs text-muted-foreground">
              No product image set. The storefront will use the category fallback:{' '}
              {getCategoryFallbackImage(selectedCategory.slug)}
            </p>
          )}
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
