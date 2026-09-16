import { useState } from 'react'
import '@/styles/landing.css'
import { useLandingData } from '@/hooks/useLandingData'
import LandingBackground from '@/components/landing/LandingBackground'
import LandingSidebar from '@/components/landing/LandingSidebar'
import LandingNavbar from '@/components/landing/LandingNavbar'
import HeroSection from '@/components/landing/HeroSection'
import StatsStrip from '@/components/landing/StatsStrip'
import HardwareCategories from '@/components/landing/HardwareCategories'
import FeaturedHardware from '@/components/landing/FeaturedHardware'
import GenerationBrowser from '@/components/landing/GenerationBrowser'
import PcBuilderPromo from '@/components/landing/PcBuilderPromo'
import RecentlyAdded from '@/components/landing/RecentlyAdded'
import HardwareSearchBand from '@/components/landing/HardwareSearchBand'
import LandingFooter from '@/components/landing/LandingFooter'

export default function LandingPage() {
  const {
    home,
    categories,
    intelGenerations,
    amdGenerations,
    loading,
    error,
    totalProducts,
    cpuCount,
    gpuCount,
    motherboardCount,
    categoryCount,
  } = useLandingData()

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false)

  const closeMobileSidebar = () => setMobileSidebarOpen(false)

  const handleSidebarToggle = () => {
    if (window.innerWidth <= 860) {
      setMobileSidebarOpen(false)
    } else {
      setSidebarCollapsed((v) => !v)
    }
  }

  const stats = [
    { value: totalProducts, label: 'Hardware Products' },
    { value: cpuCount, label: 'CPU Models' },
    { value: gpuCount, label: 'GPU Models' },
    { value: motherboardCount, label: 'Motherboards' },
    { value: categoryCount, label: 'Hardware Categories' },
  ]

  const popular = home?.popular ?? []
  const latest = home?.latest ?? []
  const builderSamples = [...popular, ...latest].slice(0, 5)

  return (
    <div className="landing-page">
      <LandingBackground />

      <div
        className={`sidebar-scrim${mobileSidebarOpen ? ' show' : ''}`}
        onClick={closeMobileSidebar}
        aria-hidden="true"
      />

      <div className="shell">
        <LandingSidebar
          categories={categories}
          collapsed={sidebarCollapsed}
          mobileOpen={mobileSidebarOpen}
          onToggle={handleSidebarToggle}
          onNavigate={closeMobileSidebar}
        />

        <div className="main">
          <LandingNavbar
            onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
            mobileSearchOpen={mobileSearchOpen}
            onToggleMobileSearch={() => setMobileSearchOpen((v) => !v)}
            onCloseMobileSearch={() => setMobileSearchOpen(false)}
          />

          <div className="page">
            {error && (
              <div className="landing-error glass" role="alert">
                <p>Unable to load some catalog data right now.</p>
                <p>{error}</p>
              </div>
            )}

            <HeroSection productCount={totalProducts} loading={loading} />

            <StatsStrip stats={stats} loading={loading} error={error} />

            {loading ? (
              <div className="landing-loading section">
                <p>Loading hardware catalog...</p>
              </div>
            ) : (
              <>
                <HardwareCategories categories={categories} />
                <FeaturedHardware products={popular} />
                <GenerationBrowser
                  intelGenerations={intelGenerations}
                  amdGenerations={amdGenerations}
                />
                <PcBuilderPromo sampleProducts={builderSamples} />
                <RecentlyAdded products={latest} />
                <HardwareSearchBand />
              </>
            )}
          </div>

          <LandingFooter />
        </div>
      </div>
    </div>
  )
}
