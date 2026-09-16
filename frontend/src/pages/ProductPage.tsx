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

  if (loading) {
    return (
      <div className="product-page mx-auto max-w-7xl px-4 sm:px-6 lg:px-10 xl:px-12 py-8 lg:py-10">
        <LoadingState count={1} />
      </div>
    )
  }
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
    <div className="product-page mx-auto max-w-7xl px-4 sm:px-6 lg:px-10 xl:px-12 py-8 lg:py-10">
      <Breadcrumbs
        className="product-breadcrumbs"
        items={[
          { label: product.category || category || '', href: getCategoryPath(category || '') },
          { label: product.manufacturer || manufacturer || '', href: getCategoryPath(category || '') + `?manufacturer=${manufacturer}` },
          { label: product.name },
        ]}
      />

      <div className="product-hero grid grid-cols-1 items-start gap-10 lg:grid-cols-3 lg:gap-12 mb-12 lg:mb-14">
        <div className="lg:col-span-2">
          <div className="product-badges flex flex-wrap gap-2.5 mb-5">
            <Badge className="px-3 py-1.5">{product.category}</Badge>
            {product.is_popular && <Badge variant="secondary" className="px-3 py-1.5">Popular</Badge>}
            {product.architecture && <Badge variant="outline" className="px-3 py-1.5">{product.architecture}</Badge>}
            {product.status && product.status !== 'active' && (
              <Badge variant="outline" className="px-3 py-1.5">{product.status}</Badge>
            )}
          </div>

          <p className="product-manufacturer text-sm text-primary font-medium mb-3">{product.manufacturer}</p>
          <h1 className="product-title text-3xl lg:text-4xl font-bold leading-[1.2] mb-5">{product.name}</h1>

          <div className="product-metadata flex flex-wrap gap-x-8 gap-y-4 text-sm text-muted-foreground mb-6">
            {product.family && (
              <span className="flex items-center gap-2.5">
                <GitBranch className="h-4 w-4 shrink-0" />
                {product.family}
              </span>
            )}
            {product.series && (
              <span className="flex items-center gap-2.5">
                <Layers className="h-4 w-4 shrink-0" />
                {product.series}
              </span>
            )}
            {product.generation && <span className="leading-relaxed">{product.generation}</span>}
            {product.release_date && (
              <span className="flex items-center gap-2.5">
                <Calendar className="h-4 w-4 shrink-0" />
                {formatDate(product.release_date)}
              </span>
            )}
          </div>

          {product.description && (
            <p className="product-description text-muted-foreground leading-[1.7] max-w-3xl mb-8">
              {product.description}
            </p>
          )}

          {quickSpecs.length > 0 && (
            <div className="product-quick-specs rounded-lg border border-border p-6 sm:p-7">
              <h3 className="product-quick-specs-title text-sm font-semibold mb-5">Quick Specifications</h3>
              <div className="product-quick-specs-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-7">
                {quickSpecs.map((spec) => (
                  <div key={spec.key} className="product-quick-spec-item">
                    <p className="product-quick-spec-label text-[0.75rem] uppercase tracking-wide text-muted-foreground leading-[1.4]">
                      {spec.display_name || spec.key}
                    </p>
                    <p className="product-quick-spec-value text-sm font-medium mt-2 leading-normal">
                      {spec.value}{spec.unit ? ` ${spec.unit}` : ''}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="product-actions flex w-full flex-col gap-3.5 lg:sticky lg:top-24 self-start">
          <HardwareImage
            product={product}
            variant="detail"
            className="product-image-card bg-card border-border p-7"
          />
          {product.images && product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-3">
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
          <Button onClick={handleCompare} variant="outline" className="w-full h-12 gap-2.5 px-5">
            <GitCompareArrows className="h-4 w-4" />
            Add to Compare
          </Button>
          <Link to="/compare" className="block">
            <Button variant="secondary" className="w-full h-12 px-5">View Comparison</Button>
          </Link>
        </div>
      </div>

      <Tabs defaultValue="specs" className="product-tabs">
        <TabsList className="product-tabs-list h-auto flex flex-wrap gap-3 p-2">
          <TabsTrigger value="specs" className="px-5 py-3">Specifications</TabsTrigger>
          <TabsTrigger value="overview" className="px-5 py-3">Overview</TabsTrigger>
          {product.sources && product.sources.length > 0 && (
            <TabsTrigger value="sources" className="px-5 py-3">Sources</TabsTrigger>
          )}
          {product.benchmarks && product.benchmarks.length > 0 && (
            <TabsTrigger value="benchmarks" className="px-5 py-3">Benchmarks</TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="specs" className="mt-8">
          {Object.keys(specGroups).length > 0 ? (
            <SpecTable groups={specGroups} />
          ) : (
            <p className="text-muted-foreground">No specifications available.</p>
          )}
        </TabsContent>

        <TabsContent value="overview" className="mt-8">
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="product-spec-table w-full text-sm">
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
                    <td className="product-spec-label font-medium text-muted-foreground w-1/3 border-r border-border">
                      {label}
                    </td>
                    <td className="product-spec-value">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        {product.sources && product.sources.length > 0 && (
          <TabsContent value="sources" className="mt-8">
            <div className="product-sources">
              <h2 className="text-lg font-semibold mb-5">Data Sources</h2>
              {product.sources.map((item) => (
                <div key={item.id} className="product-source-card rounded-lg border border-border bg-card p-4 space-y-3">
                  <p className="font-medium leading-relaxed">{item.source?.name || 'Source'}</p>
                  {item.notes && (
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.notes}</p>
                  )}
                  {(item.source_url || item.source?.url) && (
                    <a
                      href={item.source_url || item.source?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline inline-block pt-1"
                    >
                      View Source
                    </a>
                  )}
                  {item.source_date && (
                    <p className="text-xs text-muted-foreground pt-1">
                      Last Verified: {formatDate(item.source_date)}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>
        )}

        {product.benchmarks && product.benchmarks.length > 0 && (
          <TabsContent value="benchmarks" className="mt-8">
            <div className="rounded-lg border border-border overflow-hidden">
              <table className="product-spec-table w-full text-sm">
                <thead className="bg-muted/80">
                  <tr>
                    <th className="product-spec-label text-left font-medium">Benchmark</th>
                    <th className="product-spec-label text-left font-medium">Score</th>
                    <th className="product-spec-label text-left font-medium">Source</th>
                  </tr>
                </thead>
                <tbody>
                  {product.benchmarks.map((b, i) => (
                    <tr key={b.id} className={i % 2 === 0 ? 'bg-card' : 'bg-muted/20'}>
                      <td className="product-spec-value">{b.name}</td>
                      <td className="product-spec-value">{b.score}{b.unit ? ` ${b.unit}` : ''}</td>
                      <td className="product-spec-value text-muted-foreground">{b.source || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabsContent>
        )}
      </Tabs>

      {product.related_products && product.related_products.length > 0 && (
        <section className="product-related mt-12 border-t border-border pt-8 lg:mt-14 lg:pt-10">
          <h2 className="text-xl font-bold mb-6 lg:mb-8">Related Products</h2>
          <div className="product-related-grid grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {product.related_products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
