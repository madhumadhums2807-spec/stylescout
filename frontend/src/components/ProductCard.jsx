import { DemoBadge } from './DemoBadge'
import { otherStores, primaryStore } from '../services/shopLinks'

/** onShop(product, storeName): the shopper picked a store; the parent opens the in-app store view.
 *  onToggleCompare is optional (the store view's "similar" cards do not show the compare button).
 *  preferredStore makes that store the big button (used inside the store view). */
export default function ProductCard({ product, selected, onToggleCompare, compareDisabled, onShop, preferredStore, saved, onToggleSaved }) {
  const store = primaryStore(product, preferredStore)
  const others = otherStores(product, store.name)

  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl bg-white shadow-card transition duration-200 hover:-translate-y-1 hover:shadow-lift">
      <div className="relative bg-white">
        <img src={product.image_url} alt={product.name} loading="lazy" className="aspect-[3/4] w-full object-contain p-2" />
        {product.match_percent != null && (
          <span className="absolute left-2 top-2 rounded-full bg-brand-teal px-2.5 py-1 text-xs font-bold text-white shadow">
            {product.match_percent}% match
          </span>
        )}
        <div className="absolute right-2 top-2 flex flex-col gap-2">
          {onToggleSaved && (
            <button onClick={() => onToggleSaved(product)} aria-pressed={!!saved}
              aria-label={saved ? 'Remove from saved' : 'Save for later'}
              className={`grid h-9 w-9 place-items-center rounded-full shadow transition active:scale-90 ${
                saved ? 'bg-brand-pink text-white' : 'bg-white text-brand-pink hover:bg-brand-pink/10'}`}>
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill={saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21s-7.5-4.6-9.5-9.2C1 8.3 3 5 6.3 5c2 0 3.5 1.1 4.2 2.4h3C14.2 6.1 15.7 5 17.7 5 21 5 23 8.3 21.5 11.8 19.5 16.4 12 21 12 21z" />
              </svg>
            </button>
          )}
          {onToggleCompare && (
            <button onClick={() => onToggleCompare(product)} disabled={!selected && compareDisabled}
              aria-pressed={selected} aria-label={selected ? 'Remove from compare' : 'Add to compare'}
              className={`grid h-9 w-9 place-items-center rounded-full text-lg font-bold shadow transition disabled:opacity-40 ${
                selected ? 'bg-brand-pink text-white' : 'bg-white text-brand-pink hover:bg-brand-pink/10'}`}>
              {selected ? '\u2713' : '+'}
            </button>
          )}
        </div>
        {product.is_demo && <DemoBadge className="absolute bottom-2 left-2" />}
      </div>

      <div className="flex flex-1 flex-col gap-1 p-3 sm:p-4">
        <p className="text-[11px] font-bold uppercase tracking-wide text-brand-plum/50">{product.category}</p>
        <h3 className="line-clamp-2 text-sm font-bold leading-snug sm:text-base">{product.name}</h3>
        <p className="mt-1 font-display text-xl font-extrabold text-brand-plum">
          Rs {product.price.toLocaleString('en-IN')}
          <span className="ml-1.5 align-middle text-[10px] font-medium text-brand-plum/45">sample price</span>
        </p>

        <button type="button" onClick={() => onShop(product, store.name)}
          style={{ background: store.bg, color: store.fg }}
          className="mt-2 inline-flex items-center justify-center gap-1 whitespace-nowrap rounded-full px-2 py-2.5 text-[13px] font-bold shadow transition hover:brightness-110 active:scale-[.98] sm:px-3 sm:text-sm">
          Shop on {store.name}
          <span aria-hidden="true">&#8250;</span>
        </button>

        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] text-brand-plum/50">Or choose:</span>
          {others.map((o) => (
            <button key={o.name} type="button" onClick={() => onShop(product, o.name)}
              style={{ borderColor: o.bg }}
              className="rounded-full border px-2 py-0.5 text-[11px] font-bold text-brand-plum transition hover:bg-brand-plum/5">
              {o.name}
            </button>
          ))}
        </div>
      </div>
    </article>
  )
}
