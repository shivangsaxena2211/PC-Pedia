import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'
import { Calendar, Layers, GitCompareArrows, GitBranch } from 'lucide-react'
import { useProduct } from '@/hooks/useProduct'
import { useCompare } from '@/hooks/useCompare'
import Breadcrumbs from '@/components/Breadcrumbs'
import SpecTable from '@/components/SpecTable'
import ProductCard from '@/components/ProductCard'
import HardwareImage from '@/components/HardwareImage'
import LoadingState from '@/components/LoadingState'
import ErrorState from '@/components/ErrorState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatDate, getCategoryPath } from '@/lib/utils'

export default function ProductPage() {
  const { category, manufacturer, slug } = useParams<{
    category: string
    manufacturer: string
    slug: string
  }>()
  const { product, loading, error } = useProduct(category || '', manufacturer || '', slug || '')
  const { addToCompare } = useCompare()

  if (loading) return <div className="mx-auto max-w-7xl px-4 lg:px-8 py-8"><LoadingState count={1} /></div>
  if (error || !product) return <ErrorState message={error || 'Product not found'} />

  const handleCompare = () => {
    try {
      addToCompare(product)
      alert('Added to comparison!')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Cannot add to compare')
    }
  }

  const specGroups = product.specification_groups || {}
  const quickSpecs = product.specifications?.slice(0, 6) || []

  return (
    <div className="mx-auto max-w-7xl px-4 lg:px-8 py-8">
      <Breadcrumbs
        items={[
          { label: product.category || category || '', href: getCategoryPath(category || '') },
          { label: product.manufacturer || manufacturer || '', href: getCategoryPath(category || '') + `?manufacturer=${manufacturer}` },
          { label: product.name },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div className="lg:col-span-2">
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge>{product.category}</Badge>
            {product.is_popular && <Badge variant="secondary">Popular</Badge>}
            {product.architecture && <Badge variant="outline">{product.architecture}</Badge>}
            {product.status && product.status !== 'active' && (
              <Badge variant="outline">{product.status}</Badge>
            )}
          </div>

          <p className="text-sm text-primary font-medium mb-1">{product.manufacturer}</p>
          <h1 className="text-3xl lg:text-4xl font-bold mb-4">{product.name}</h1>

          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-6">
            {product.family && (
              <span className="flex items-center gap-1.5">
                <GitBranch className="h-4 w-4" />
                {product.family}
              </span>
            )}
            {product.series && (
              <span className="flex items-center gap-1.5">
                <Layers className="h-4 w-4" />
                {product.series}
              </span>
            )}
            {product.generation && <span>{product.generation}</span>}
            {product.release_date && (
              <span className="flex items-center gap-1.5">
                <Calendar className="h-4 w-4" />
                {formatDate(product.release_date)}
              </span>
            )}
          </div>

          {product.description && (
            <p className="text-muted-foreground leading-relaxed mb-6">{product.description}</p>
          )}

          {quickSpecs.length > 0 && (
            <div className="rounded-lg border border-border p-4 mb-6">
              <h3 className="text-sm font-semibold mb-3">Quick Specifications</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {quickSpecs.map((spec) => (
                  <div key={spec.key}>
                    <p className="text-xs text-muted-foreground">{spec.key}</p>
                    <p className="text-sm font-medium">
                      {spec.value}{spec.unit ? ` ${spec.unit}` : ''}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <HardwareImage product={product} variant="detail" className="bg-card border-border" />
          {product.images && product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.slice(0, 4).map((img) => (
                <HardwareImage
                  key={img.id}
                  product={{ ...product, primary_image_url: img.url, image_url: img.url }}
                  variant="thumbnail"
                  alt={img.alt_text || product.name}
                />
              ))}
            </div>
          )}
          <Button onClick={handleCompare} variant="outline" className="w-full gap-2">
            <GitCompareArrows className="h-4 w-4" />
            Add to Compare
          </Button>
          <Link to="/compare">
            <Button variant="secondary" className="w-full">View Comparison</Button>
          </Link>
        </div>
      </div>

      <Tabs defaultValue="specs">
        <TabsList>
          <TabsTrigger value="specs">Specifications</TabsTrigger>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          {product.benchmarks && product.benchmarks.length > 0 && (
            <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="specs" className="mt-6">
          {Object.keys(specGroups).length > 0 ? (
            <SpecTable groups={specGroups} />
          ) : (
            <p className="text-muted-foreground">No specifications available.</p>
          )}
        </TabsContent>

        <TabsContent value="overview" className="mt-6">
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <tbody>
                {[
                  ['Product Name', product.name],
                  ['Manufacturer', product.manufacturer],
                  ['Family', product.family],
                  ['Category', product.category],
                  ['Series', product.series],
                  ['Generation', product.generation],
                  ['Architecture', product.architecture],
                  ['Release Date', formatDate(product.release_date)],
                ].filter(([, v]) => v).map(([label, value], i) => (
                  <tr key={label} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/30'}>
                    <td className="px-4 py-3 font-medium text-muted-foreground w-1/3 border-r border-border">
                      {label}
                    </td>
                    <td className="px-4 py-3">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        {product.benchmarks && product.benchmarks.length > 0 && (
          <TabsContent value="benchmarks" className="mt-6">
            <div className="rounded-lg border border-border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-2 text-left">Benchmark</th>
                    <th className="px-4 py-2 text-left">Score</th>
                    <th className="px-4 py-2 text-left">Source</th>
                  </tr>
                </thead>
                <tbody>
                  {product.benchmarks.map((b, i) => (
                    <tr key={b.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                      <td className="px-4 py-3">{b.name}</td>
                      <td className="px-4 py-3">{b.score}{b.unit ? ` ${b.unit}` : ''}</td>
                      <td className="px-4 py-3 text-muted-foreground">{b.source || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabsContent>
        )}
      </Tabs>

      {product.related_products && product.related_products.length > 0 && (
        <section className="mt-12 border-t border-border pt-8">
          <h2 className="text-xl font-bold mb-6">Related Products</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {product.related_products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
