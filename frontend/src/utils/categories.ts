import type { CategoryConfig } from '@/types'
import {
  Cpu, Gpu, MemoryStick, CircuitBoard, HardDrive, Plug,
  Fan, Droplets, Wind, Box, GitCompareArrows,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export const CATEGORIES: CategoryConfig[] = [
  { slug: 'cpu', name: 'CPU', apiEndpoint: 'cpus', description: 'Central Processing Units', icon: 'cpu' },
  { slug: 'gpu', name: 'GPU', apiEndpoint: 'gpus', description: 'Graphics Processing Units', icon: 'gpu' },
  { slug: 'ram', name: 'RAM', apiEndpoint: 'ram', description: 'Memory Modules', icon: 'ram' },
  { slug: 'motherboards', name: 'Motherboard', apiEndpoint: 'motherboards', description: 'Motherboards', icon: 'motherboard' },
  { slug: 'ssd', name: 'SSD', apiEndpoint: 'ssds', description: 'Solid State Drives', icon: 'ssd' },
  { slug: 'psu', name: 'PSU', apiEndpoint: 'psus', description: 'Power Supply Units', icon: 'psu' },
  { slug: 'coolers', name: 'CPU Cooler', apiEndpoint: 'coolers', description: 'Air CPU Coolers', icon: 'cooler' },
  { slug: 'aio', name: 'AIO', apiEndpoint: 'aios', description: 'All-in-One Liquid Coolers', icon: 'aio' },
  { slug: 'fans', name: 'Fans', apiEndpoint: 'fans', description: 'Case Fans', icon: 'fans' },
  { slug: 'cases', name: 'Cases', apiEndpoint: 'cases', description: 'PC Cases', icon: 'cases' },
]

export const NAV_ITEMS = [
  { label: 'HOME', path: '/' },
  { label: 'CPU', path: '/cpu' },
  { label: 'GPU', path: '/gpu' },
  { label: 'RAM', path: '/ram' },
  { label: 'MOTHERBOARDS', path: '/motherboards' },
  { label: 'SSD', path: '/ssd' },
  { label: 'PSU', path: '/psu' },
  { label: 'COOLERS', path: '/coolers' },
  { label: 'AIO', path: '/aio' },
  { label: 'FANS', path: '/fans' },
  { label: 'CASES', path: '/cases' },
  { label: 'COMPARE', path: '/compare' },
]

const ICON_MAP: Record<string, LucideIcon> = {
  cpu: Cpu,
  gpu: Gpu,
  ram: MemoryStick,
  motherboard: CircuitBoard,
  ssd: HardDrive,
  psu: Plug,
  cooler: Fan,
  aio: Droplets,
  fans: Wind,
  cases: Box,
  compare: GitCompareArrows,
}

export function getCategoryIcon(icon: string): LucideIcon {
  return ICON_MAP[icon] || Box
}

export function getCategoryBySlug(slug: string): CategoryConfig | undefined {
  return CATEGORIES.find((c) => c.slug === slug)
}

export function getCategoryByPath(path: string): CategoryConfig | undefined {
  const slug = path.replace('/', '')
  return getCategoryBySlug(slug)
}
