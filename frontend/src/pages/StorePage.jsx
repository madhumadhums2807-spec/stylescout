import { useEffect, useRef, useState } from 'react'
import ProductCard from '../components/ProductCard'
import { DemoBadge } from '../components/DemoBadge'
import { STORES } from '../services/shopLinks'
import { getSimilar } from '../services/api'

/** In-app "store view": the dress the shopper picked comes first, similar dresses follow below.
 *  The real store cannot be shown inside our app, so "Continue" opens that store's own search in a new tab. */
export default function StorePage({ product, storeName, onClose, onShop, savedIds = [], onToggleSaved }) {
  const store = STORES[storeName] ?? STORES.Amazon
  const href = store.url(product.name)
  const scroller = useRef(null)
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true); setError(''); setSimilar([])
    scroller.current?.scrollTo({ top: 0 })
    getSimilar(product.id, 12)
      .then((d) => !cancelled && setSimilar(d))
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [product.id])

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div ref={scroller} className="fixed inset-0 z-50 overflow-y-auto bg-brand-mist" role="dialog" aria-modal="true" aria-label={`Shopping via ${store.name}`}>
      <div className="sticky top-0 z-10 flex items-center justify-between gap-3 bg-gradient-to-r from-brand-pink via-rose-500 to-brand-orange px-4 py-3 text-white shadow-md">
        <button onClick={onClose} className="inline-flex items-center gap-1 rounded-full bg-white/20 px-4 py-2 text-sm font-bold hover:bg-white/30">
          <span aria-hidden="true">&#8249;</span> Back to results
        </button>
        <span className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-sm font-bold text-brand-plum">
          <span className="h-3 w-3 rounded-full" style={{ background: store.bg }} /> Shopping via {store.name}
        </span>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-6">
        <section aria-label="Your pick" className="grid gap-6 rounded-3xl bg-white p-4 shadow-card sm:p-6 md:grid-cols-[minmax(0,320px)_1fr]">
          <div className="relative">
            <img src={product.image_url} alt={product.name} className="aspect-[3/4] w-full rounded-2xl bg-white object-contain" />
            {product.is_demo && <DemoBadge className="absolute bottom-3 left-3" />}
            {onToggleSaved && (
              <button onClick={() => onToggleSaved(product)} aria-pressed={savedIds.includes(product.id)}
                className={`absolute right-3 top-3 inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-bold shadow ${
                  savedIds.includes(product.id) ? 'bg-brand-pink text-white' : 'bg-white text-brand-pink'}`}>
                {savedIds.includes(product.id) ? '\u2665 Saved' : '\u2661 Save'}
              </button>
            )}
          </div>
          <div className="flex min-w-0 flex-col gap-3">
            <p className="pill w-fit bg-brand-teal/10 text-brand-teal">Your pick</p>
            <h1 className="font-display text-2xl font-extrabold leading-tight sm:text-3xl">{product.name}</h1>
            <div className="flex flex-wrap gap-2 text-xs font-bold">
              <span className="pill bg-brand-pink/10 capitalize text-brand-pink">{product.category}</span>
              {product.color && <span className="pill bg-brand-orange/15 capitalize text-orange-700">{product.color}</span>}
              {product.gender && <span className="pill bg-brand-plum/5 text-brand-plum">{product.gender}</span>}
              {product.usage && <span className="pill bg-brand-plum/5 text-brand-plum">{product.usage}</span>}
            </div>
            <p className="font-display text-3xl font-extrabold">
              Rs {product.price.toLocaleString('en-IN')}
              <span className="ml-2 align-middle text-xs font-medium text-brand-plum/45">sample price</span>
            </p>
            <p className="text-sm text-brand-plum/70">{product.description}</p>

            <a href={href} target="_blank" rel="noopener noreferrer" style={{ background: store.bg, color: store.fg }}
              className="mt-1 inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-base font-bold shadow-md transition hover:brightness-110 active:scale-[.98]">
              Continue to {store.name} <span aria-hidden="true">&#8599;</span>
            </a>
            <p className="text-xs text-brand-plum/55">
              Opens {store.name}'s own search for this item in a new tab. Price and availability there may differ from the sample price shown here.
            </p>
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-brand-plum/55">Prefer another store?</span>
              {Object.values(STORES).filter((s) => s.name !== store.name).map((s) => (
                <button key={s.name} onClick={() => onShop(product, s.name)} style={{ borderColor: s.bg }}
                  className="rounded-full border-2 px-3 py-1 font-bold transition hover:bg-brand-plum/5">{s.name}</button>
              ))}
            </div>
          </div>
        </section>

        <section aria-label="Similar styles" className="mt-8">
          <h2 className="mb-3 font-display text-xl font-bold">
            More <span className="capitalize">{product.category}</span> styles like this
          </h2>
          {loading && (
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4" aria-hidden="true">
              {[0, 1, 2, 3].map((i) => <div key={i} className="aspect-[3/4] animate-pulse rounded-2xl bg-brand-pink/10" />)}
            </div>
          )}
          {error && <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm font-medium text-red-800">{error}</p>}
          {!loading && !error && similar.length === 0 && <p className="text-brand-plum/60">No similar items found.</p>}
          <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4">
            {similar.map((p) => (
              <ProductCard key={p.id} product={p} preferredStore={store.name} onShop={onShop}
                saved={savedIds.includes(p.id)} onToggleSaved={onToggleSaved} />
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
