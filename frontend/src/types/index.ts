export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  icon?: string
  display_order?: number
  product_count?: number
}

export interface Manufacturer {
  id: number
  name: string
  slug: string
  logo_url?: string
  website?: string
  description?: string
  display_order?: number
  product_count?: number
}

export interface Family {
  id: number
  name: string
  slug: string
  manufacturer_id: number
  manufacturer?: string
  manufacturer_slug?: string
  category_id: number
  category_slug?: string
  description?: string
  display_order?: number
}

export interface Series {
  id: number
  name: string
  slug: string
  family_id?: number
  family?: string
  family_slug?: string
  manufacturer_id: number
  manufacturer?: string
  manufacturer_slug?: string
  category_id: number
  category_slug?: string
  description?: string
  display_order?: number
}

export interface Generation {
  id: number
  name: string
  slug: string
  series_id: number
  series?: string
  series_slug?: string
  architecture?: string
  release_year?: number
  release_date?: string
  description?: string
  display_order?: number
}

export interface SpecificationDefinition {
  id: number
  category_id: number
  group_name: string
  key: string
  display_name: string
  data_type: string
  unit?: string
  filterable: boolean
  comparable: boolean
  required: boolean
  display_order: number
}

export interface Specification {
  id: number
  group_name: string
  key: string
  display_name?: string
  value: string
  unit?: string
  sort_order: number
}

export interface DataSource {
  id: number
  name: string
  slug: string
  url?: string
  description?: string
}

export interface ProductSource {
  id: number
  product_id: number
  source_id: number
  source_url?: string
  source_date?: string
  notes?: string
  source?: DataSource
}

export interface Product {
  id: number
  name: string
  slug: string
  url_path?: string
  manufacturer_id: number
  manufacturer?: string
  manufacturer_slug?: string
  category_id: number
  category?: string
  category_slug?: string
  family_id?: number
  family?: string
  family_slug?: string
  series_id?: number
  series?: string
  series_slug?: string
  generation_id?: number
  generation?: string
  generation_slug?: string
  architecture?: string
  description?: string
  release_date?: string
  image_url?: string
  primary_image_url?: string
  status?: string
  is_popular?: boolean
  created_at?: string
  updated_at?: string
  quick_specs?: Record<string, string>
  specifications?: Specification[]
  specification_groups?: Record<string, Specification[]>
  images?: ProductImage[]
  benchmarks?: Benchmark[]
  related_products?: Product[]
  sources?: ProductSource[]
}

export interface ProductSourceInput {
  name: string
  url?: string
  date?: string
  notes?: string
}

export interface ProductImage {
  id: number
  url: string
  alt_text?: string
  image_type?: string
  is_primary: boolean
  sort_order: number
}

export interface ProductImageInput {
  url: string
  alt_text?: string
  image_type?: string
  is_primary?: boolean
  sort_order?: number
}

export interface Benchmark {
  id: number
  name: string
  score?: number
  unit?: string
  source?: string
  notes?: string
}

export interface Pagination {
  page: number
  limit?: number
  per_page?: number
  total: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ProductListResponse {
  data: Product[]
  items?: Product[]  // backward compat
  pagination: Pagination
  filters?: FilterOptions
}

export interface FilterOptions {
  manufacturers: Manufacturer[]
  families: Family[]
  series: Series[]
  generations: Generation[]
  specification_definitions?: SpecificationDefinition[]
  filterable_specifications?: SpecificationDefinition[]
}

export interface SearchResult {
  id: number
  name: string
  slug: string
  url_path?: string
  category?: string
  category_slug?: string
  manufacturer?: string
  manufacturer_slug?: string
  family?: string
  series?: string
  generation?: string
  architecture?: string
  image_url?: string
}

export interface ComparisonRow {
  group: string
  key: string
  display_name?: string
  values: Record<string, string>
  all_same?: boolean
}

export interface ComparisonResponse {
  category: string
  category_slug?: string
  products: Product[]
  comparison: ComparisonRow[]
}

export interface HomeData {
  popular: Product[]
  latest: Product[]
  manufacturers: Manufacturer[]
}

export interface CategoryConfig {
  slug: string
  name: string
  apiEndpoint: string
  description: string
  icon: string
}
