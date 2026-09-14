import api from './api'
import type {
  Category,
  Manufacturer,
  Family,
  Series,
  Generation,
  Product,
  ProductListResponse,
  SearchResult,
  ComparisonResponse,
  HomeData,
  SpecificationDefinition,
} from '@/types'

export interface ProductQueryParams {
  page?: number
  limit?: number
  category?: string
  manufacturer?: string
  family?: string
  series?: string
  generation?: string
  sort?: string
  order?: 'asc' | 'desc'
  search?: string
  architecture?: string
  popular?: boolean
  [key: string]: string | number | boolean | undefined
}

// ─── Categories & Taxonomy ───────────────────────────────────────────────────

export async function getCategories(): Promise<Category[]> {
  const { data } = await api.get('/categories')
  return data.data
}

export async function getCategory(slug: string): Promise<Category> {
  const { data } = await api.get(`/categories/${slug}`)
  return data
}

export async function getFamilies(categorySlug: string, manufacturer?: string): Promise<Family[]> {
  const params = manufacturer ? { manufacturer } : {}
  const { data } = await api.get(`/categories/${categorySlug}/families`, { params })
  return data.data
}

export async function getSeries(
  categorySlug: string,
  family?: string,
  manufacturer?: string,
): Promise<Series[]> {
  const params: Record<string, string> = {}
  if (family) params.family = family
  if (manufacturer) params.manufacturer = manufacturer
  const { data } = await api.get(`/categories/${categorySlug}/series`, { params })
  return data.data
}

export async function getGenerations(
  categorySlug: string,
  series?: string,
  family?: string,
): Promise<Generation[]> {
  const params: Record<string, string> = {}
  if (series) params.series = series
  if (family) params.family = family
  const { data } = await api.get(`/categories/${categorySlug}/generations`, { params })
  return data.data
}

export async function getSpecificationDefinitions(
  categorySlug: string,
): Promise<SpecificationDefinition[]> {
  const { data } = await api.get(`/categories/${categorySlug}/specification-definitions`)
  return data.data
}

// ─── Products ────────────────────────────────────────────────────────────────

export async function getHomeData(): Promise<HomeData> {
  const { data } = await api.get('/home')
  return data
}

export async function getManufacturers(category?: string): Promise<Manufacturer[]> {
  const params = category ? { category } : {}
  const { data } = await api.get('/manufacturers', { params })
  return data.data ?? data.items ?? []
}

export async function getProducts(
  endpointOrParams: string | ProductQueryParams,
  params: ProductQueryParams = {},
): Promise<ProductListResponse> {
  if (typeof endpointOrParams === 'string') {
    const { data } = await api.get(`/${endpointOrParams}`, { params })
    return normalizeListResponse(data)
  }
  const { data } = await api.get('/products', { params: endpointOrParams })
  return normalizeListResponse(data)
}

export async function getProductByPath(
  category: string,
  manufacturer: string,
  slug: string,
): Promise<Product> {
  const { data } = await api.get(`/products/${category}/${manufacturer}/${slug}`)
  return data
}

export async function getProduct(slug: string): Promise<Product> {
  const { data } = await api.get(`/products/by-slug/${slug}`)
  return data
}

export async function getProductById(id: number): Promise<Product> {
  const { data } = await api.get(`/products/${id}`)
  return data
}

export async function searchProducts(query: string, limit = 20): Promise<SearchResult[]> {
  const { data } = await api.get('/search', { params: { q: query, limit } })
  return data.items
}

export async function compareProducts(slugs: string[]): Promise<ComparisonResponse> {
  const { data } = await api.get('/compare', {
    params: { products: slugs.join(',') },
  })
  return data
}

function normalizeListResponse(data: Record<string, unknown>): ProductListResponse {
  const items = (data.data ?? data.items) as Product[]
  return {
    data: items,
    items,
    pagination: data.pagination as ProductListResponse['pagination'],
    filters: data.filters as ProductListResponse['filters'],
  }
}

// Map category slug to legacy API endpoint
export const CATEGORY_API_MAP: Record<string, string> = {
  cpu: 'cpus',
  gpu: 'gpus',
  ram: 'ram',
  motherboards: 'motherboards',
  ssd: 'ssds',
  psu: 'psus',
  coolers: 'coolers',
  aio: 'aios',
  fans: 'fans',
  cases: 'cases',
}

export function getCategoryApiEndpoint(slug: string): string {
  return CATEGORY_API_MAP[slug] ?? slug
}

// ─── Admin API ───────────────────────────────────────────────────────────────

export async function getAdminDashboard() {
  const { data } = await api.get('/admin/dashboard')
  return data
}

export async function getAdminProducts(): Promise<Product[]> {
  const { data } = await api.get('/admin/products')
  return data.data ?? data.items ?? []
}

export async function createProduct(productData: Record<string, unknown>): Promise<Product> {
  const { data } = await api.post('/admin/products', productData)
  return data
}

export async function createManufacturer(data: Record<string, unknown>): Promise<Manufacturer> {
  const { data: result } = await api.post('/admin/manufacturers', data)
  return result
}

export async function createFamily(data: Record<string, unknown>): Promise<Family> {
  const { data: result } = await api.post('/admin/families', data)
  return result
}

export async function createSeries(data: Record<string, unknown>): Promise<Series> {
  const { data: result } = await api.post('/admin/series', data)
  return result
}

export async function createGeneration(data: Record<string, unknown>): Promise<Generation> {
  const { data: result } = await api.post('/admin/generations', data)
  return result
}

export async function getAdminManufacturers(): Promise<Manufacturer[]> {
  const { data } = await api.get('/admin/manufacturers')
  return data.data ?? data.items ?? []
}

export async function getAdminFamilies(): Promise<Family[]> {
  const { data } = await api.get('/admin/families')
  return data.data ?? []
}

export async function getAdminSeries(): Promise<Series[]> {
  const { data } = await api.get('/admin/series')
  return data.data ?? data.items ?? []
}

export async function getAdminGenerations(): Promise<Generation[]> {
  const { data } = await api.get('/admin/generations')
  return data.data ?? data.items ?? []
}

export async function getAdminCategories(): Promise<Category[]> {
  const { data } = await api.get('/admin/categories')
  return data.data ?? data.items ?? []
}

export async function getAdminSpecDefinitions(categoryId?: number): Promise<SpecificationDefinition[]> {
  const params = categoryId ? { category_id: categoryId } : {}
  const { data } = await api.get('/admin/specification-definitions', { params })
  return data.data ?? []
}
