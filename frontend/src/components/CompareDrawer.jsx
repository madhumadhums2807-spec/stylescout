import { DemoBadge } from './DemoBadge'
import { primaryStore } from '../services/shopLinks'

/** Slide-over panel that shows 2-4 chosen products side by side (data comes from POST /api/compare). */
export default function CompareDrawer({ open, onClose, items, data, loading, error, onRemove }) {
  if (!open) return null
  const rows = [
    ['Price', (p) => `Rs ${p.price.toLocaleString('en-IN')}`],
    ['Platform', (p) => p.platform],
    ['Category', (p) => p.category],
    ['Colour', (p) => p.color],
    ['For', (p) => p.gender],
    ['Occasion', (p) => p.usage],
  ]
  const products = data?.products ?? []

  return (
    <div className="fixed inset-0 z-40 flex justify-end" role="dialog" aria-modal="true" aria-label="Compare products">
      <div className="absolute inset-0 bg-brand-plum/50" onClick={onClose} />
      <div className="relative flex h-full w-full max-w-3xl flex-col overflow-y-auto bg-brand-mist p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-2xl font-extrabold">Compare</h2>
          <button className="btn btn-ghost" onClick={onClose}>Close</button>
        </div>

        {items.length < 2 && <p className="text-brand-plum/60">Pick at least two products with the Compare button on each card.</p>}
        {loading && <p className="text-brand-plum/60">Loading comparison...</p>}
        {error && <p role="alert" className="text-red-700">{error}</p>}

        {items.length >= 2 && products.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[480px] border-separate border-spacing-x-3 text-sm">
              <thead>
                <tr>
                  <th />
                  {products.map((p) => (
                    <th key={p.id} className="w-1/4 align-top font-normal">
                      <img src={p.image_url} alt={p.name} className="mx-auto aspect-[3/4] w-full rounded-xl bg-white object-contain shadow-card" />
                      <p className="mt-2 font-medium">{p.name}</p>
                      {p.is_demo && <DemoBadge />}
                      <button onClick={() => onRemove(p.id)} className="mt-1 block text-xs font-bold text-brand-pink underline">Remove</button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map(([label, get]) => (
                  <tr key={label}>
                    <td className="py-2 pr-2 text-brand-plum/60">{label}</td>
                    {products.map((p) => (
                      <td key={p.id} className={`py-2 text-center capitalize ${label === 'Price' && p.id === data.cheapest_id ? 'font-bold text-brand-teal' : ''}`}>
                        {get(p)}{label === 'Price' && p.id === data.cheapest_id ? ' (lowest)' : ''}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr>
                  <td className="py-3 pr-2 text-brand-plum/60">Shop</td>
                  {products.map((p) => {
                    const st = primaryStore(p)
                    return (
                      <td key={p.id} className="py-3 text-center">
                        <a href={st.href} target="_blank" rel="noopener noreferrer" style={{ background: st.bg, color: st.fg }}
                          className="inline-block rounded-full px-3 py-1.5 text-xs font-bold shadow">Shop on {st.name} &#8599;</a>
                      </td>
                    )
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
