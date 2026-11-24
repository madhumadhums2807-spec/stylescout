import { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import CompareDrawer from './components/CompareDrawer'
import { DemoBanner } from './components/DemoBadge'
import Home from './pages/Home'
import Results from './pages/Results'
import StorePage from './pages/StorePage'
import Saved from './pages/Saved'
import { useWishlist } from './hooks/useWishlist'
import { defaultFilters } from './services/facets'
import { compareProducts, searchByImage } from './services/api'

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | done
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [filters, setFilters] = useState({ minPrice: 0, maxPrice: 0, selected: [], categories: [], colours: [], genders: [], usages: [], sort: 'match' })
  const wishlist = useWishlist()
  const [view, setView] = useState('main') // main | saved

  const [shop, setShop] = useState(null) // { product, storeName } while the in-app store view is open

  const [compareItems, setCompareItems] = useState([])
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [compareData, setCompareData] = useState(null)
  const [compareLoading, setCompareLoading] = useState(false)
  const [compareError, setCompareError] = useState('')

  // free the temporary blob URL when the preview changes
  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl])

  function selectFile(f) {
    setFile(f)
    setPreviewUrl(URL.createObjectURL(f))
    setError('')
  }
  function clearFile() { setFile(null); setPreviewUrl(''); setError('') }

  async function runSearch() {
    setStatus('loading'); setError('')
    try {
      const data = await searchByImage(file, { topK: 200 }) // no filters: we filter locally afterwards
      setFilters(defaultFilters(data.results))
      setResult(data)
      setCompareItems([])
      setStatus('done')
    } catch (e) {
      setError(e.message === 'Failed to fetch' ? 'Cannot reach the server. Is the backend running on port 8000?' : e.message)
      setStatus('idle')
    }
  }

  function newSearch() { setView('main'); setStatus('idle'); setResult(null); clearFile() }

  function toggleCompare(product) {
    setCompareItems((items) =>
      items.some((p) => p.id === product.id) ? items.filter((p) => p.id !== product.id) : [...items, product])
  }

  // fetch the side-by-side data from the API whenever the drawer is open with 2+ items
  useEffect(() => {
    if (!drawerOpen || compareItems.length < 2) { setCompareData(null); return }
    let cancelled = false
    setCompareLoading(true); setCompareError('')
    compareProducts(compareItems.map((p) => p.id))
      .then((d) => !cancelled && setCompareData(d))
      .catch((e) => !cancelled && setCompareError(e.message))
      .finally(() => !cancelled && setCompareLoading(false))
    return () => { cancelled = true }
  }, [drawerOpen, compareItems])

  const priceBounds = result
    ? [Math.floor(Math.min(...result.results.map((p) => p.price)) / 50) * 50, Math.ceil(Math.max(...result.results.map((p) => p.price)) / 50) * 50]
    : [0, 0]

  return (
    <div className="min-h-screen">
      <DemoBanner />
      <Navbar onHome={newSearch} compareCount={compareItems.length} onOpenCompare={() => setDrawerOpen(true)}
        savedCount={wishlist.items.length} onOpenSaved={() => setView('saved')} />
      <main>
        {view === 'saved' ? (
          <Saved items={wishlist.items} onToggleSaved={wishlist.toggle} onClear={wishlist.clear}
            onShop={(product, storeName) => setShop({ product, storeName })} onBack={() => setView('main')} />
        ) : status === 'done' && result ? (
          <Results result={result} previewUrl={previewUrl} filters={filters} setFilters={setFilters}
            priceBounds={priceBounds} savedIds={wishlist.ids} onToggleSaved={wishlist.toggle} compareIds={compareItems.map((p) => p.id)}
            onToggleCompare={toggleCompare} onNewSearch={newSearch}
            onShop={(product, storeName) => setShop({ product, storeName })} />
        ) : (
          <Home file={file} previewUrl={previewUrl} onSelect={selectFile} onClear={clearFile}
            onSearch={runSearch} loading={status === 'loading'} error={error} />
        )}
      </main>
      {shop && (
        <StorePage product={shop.product} storeName={shop.storeName} onClose={() => setShop(null)}
          savedIds={wishlist.ids} onToggleSaved={wishlist.toggle}
          onShop={(product, storeName) => setShop({ product, storeName })} />
      )}
      <CompareDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} items={compareItems} data={compareData}
        loading={compareLoading} error={compareError} onRemove={(id) => setCompareItems((i) => i.filter((p) => p.id !== id))} />
      <footer className="px-4 py-8 text-center text-xs text-brand-plum/50">
        StyleScout mini project - sample data only. Prices and platforms are placeholders.
      </footer>
    </div>
  )
}
