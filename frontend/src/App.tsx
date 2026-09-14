import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from '@/layouts/MainLayout'
import HomePage from '@/pages/HomePage'
import CategoryPage from '@/pages/CategoryPage'
import ProductPage from '@/pages/ProductPage'
import ComparePage from '@/pages/ComparePage'
import AdminLayout from '@/pages/admin/AdminLayout'
import AdminDashboard from '@/pages/admin/AdminDashboard'
import AdminProducts from '@/pages/admin/AdminProducts'
import AdminProductForm from '@/pages/admin/AdminProductForm'
import AdminManufacturers from '@/pages/admin/AdminManufacturers'
import AdminSeries from '@/pages/admin/AdminSeries'
import AdminGenerations from '@/pages/admin/AdminGenerations'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="products" element={<AdminProducts />} />
            <Route path="products/new" element={<AdminProductForm />} />
            <Route path="manufacturers" element={<AdminManufacturers />} />
            <Route path="series" element={<AdminSeries />} />
            <Route path="generations" element={<AdminGenerations />} />
          </Route>
          {/* Dynamic category pages - loaded from API */}
          <Route path="/:category" element={<CategoryPage />} />
          {/* Product pages: /cpu/amd/ryzen-7-7800x3d */}
          <Route path="/:category/:manufacturer/:slug" element={<ProductPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
