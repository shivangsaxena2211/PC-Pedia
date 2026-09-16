import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { Category } from '@/types'
import { getCategoryIcon } from '@/utils/categories'
import { getCategoryPath } from '@/lib/utils'

interface HardwareCategoriesProps {
  categories: Category[]
}

export default function HardwareCategories({ categories }: HardwareCategoriesProps) {
  const gridRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const cards = gridRef.current?.querySelectorAll('.cat-card')
    if (!cards?.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in')
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15 },
    )

    cards.forEach((card) => observer.observe(card))
    return () => observer.disconnect()
  }, [categories])

  return (
    <section className="section" id="categories">
      <div className="section-head">
        <div>
          <h2>Explore Hardware</h2>
          <p>Browse the component database by category</p>
        </div>
      </div>
      <div className="cat-grid" ref={gridRef}>
        {categories.map((cat, index) => {
          const Icon = getCategoryIcon(cat.icon || cat.slug)
          const count = cat.product_count ?? 0
          return (
            <Link
              key={cat.id}
              to={getCategoryPath(cat.slug)}
              className="cat-card glass"
              style={{ transitionDelay: `${index * 40}ms` }}
            >
              <div className="cat-icon">
                <Icon aria-hidden="true" />
              </div>
              <h3>{cat.name}</h3>
              <div className="cat-sub">{cat.description || 'Hardware category'}</div>
              <div className="cat-foot">
                <span className="cat-count">
                  {count} {count === 1 ? 'product' : 'products'}
                </span>
                <span className="cat-cta">
                  Explore <ArrowRight aria-hidden="true" />
                </span>
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
