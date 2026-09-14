import { Link } from 'react-router-dom'
import type { CategoryConfig } from '@/types'
import { getCategoryIcon } from '@/utils/categories'
import { Card, CardContent } from './ui/card'

interface CategoryCardProps {
  category: CategoryConfig
}

export default function CategoryCard({ category }: CategoryCardProps) {
  const Icon = getCategoryIcon(category.icon)

  return (
    <Link to={`/${category.slug}`}>
      <Card className="group hover:border-primary/50 transition-all duration-200 hover:shadow-md hover:shadow-primary/5 h-full">
        <CardContent className="p-6 flex flex-col items-center text-center gap-3">
          <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
            <Icon className="h-8 w-8" />
          </div>
          <div>
            <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
              {category.name}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">{category.description}</p>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
