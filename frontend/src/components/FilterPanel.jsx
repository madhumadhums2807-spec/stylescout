/** Controlled filter form: the parent owns the state, this just renders and reports changes. */
const STORE_DOT = { Myntra: '#ff3f6c', Ajio: '#2c4152', Meesho: '#9f2089', Flipkart: '#2874f0', Amazon: '#ffb100' }
const COLOUR_DOT = {
  black: '#111', white: '#fff', grey: '#9ca3af', blue: '#2563eb', navy: '#1e2a5a', red: '#dc2626', pink: '#f472b6',
  green: '#16a34a', yellow: '#facc15', orange: '#fb923c', purple: '#7e22ce', brown: '#78350f', beige: '#e5d3b3',
  cream: '#fff7d6', olive: '#6b7a2a', maroon: '#7f1d1d', teal: '#0f766e', gold: '#d4af37', silver: '#c0c0c0',
  multicolour: 'conic-gradient(#ef4444,#facc15,#22c55e,#3b82f6,#a855f7,#ef4444)',
}

function Chips({ title, options, chosen, onToggle, dot, empty }) {
  if (options.length === 0) return null
  return (
    <div>
      <h2 className="mb-2 font-display text-base font-bold">{title}</h2>
      <div className="flex flex-wrap gap-2">
        {options.map(({ value, count }) => {
          const on = chosen.includes(value)
          return (
            <button key={value} onClick={() => onToggle(value)} aria-pressed={on}
              className={`inline-flex items-center gap-1.5 rounded-full border-2 px-3 py-1 text-sm font-bold capitalize transition ${
                on ? 'border-brand-pink bg-brand-pink text-white' : 'border-brand-plum/15 bg-white hover:border-brand-pink/50'}`}>
              {dot && <span className="h-3 w-3 rounded-full border border-black/15" style={{ background: dot(value) }} />}
              {value}
              {count != null && <span className={`text-[11px] font-medium ${on ? 'text-white/80' : 'text-brand-plum/45'}`}>{count}</span>}
            </button>
          )
        })}
      </div>
      {empty && chosen.length === 0 && <p className="mt-2 text-xs text-brand-plum/50">{empty}</p>}
    </div>
  )
}

export default function FilterPanel({ filters, setFilters, facets, priceBounds, resultCount, totalCount, activeCount, onClear }) {
  const { minPrice, maxPrice } = filters
  const [lo, hi] = priceBounds

  const toggle = (key) => (value) =>
    setFilters({ ...filters, [key]: filters[key].includes(value) ? filters[key].filter((x) => x !== value) : [...filters[key], value] })

  return (
    <aside className="space-y-6 rounded-2xl bg-white p-5 shadow-card lg:sticky lg:top-20 lg:self-start">
      <div className="flex items-center justify-between">
        <p className="text-sm text-brand-plum/60">Showing <strong className="text-brand-plum">{resultCount}</strong> of {totalCount}</p>
        {activeCount > 0 && (
          <button onClick={onClear} className="text-sm font-bold text-brand-pink hover:underline">Clear all ({activeCount})</button>
        )}
      </div>

      <div>
        <h2 className="mb-1 font-display text-base font-bold">Budget</h2>
        <p className="mb-3 inline-block rounded-full bg-brand-pink/10 px-3 py-1 text-sm font-bold text-brand-pink">
          Rs {minPrice.toLocaleString('en-IN')} - Rs {maxPrice.toLocaleString('en-IN')}
        </p>
        <label className="block text-xs text-brand-plum/60">Minimum
          <input type="range" min={lo} max={hi} step={50} value={minPrice} className="w-full accent-brand-pink"
            onChange={(e) => setFilters({ ...filters, minPrice: Math.min(Number(e.target.value), maxPrice) })} />
        </label>
        <label className="block text-xs text-brand-plum/60">Maximum
          <input type="range" min={lo} max={hi} step={50} value={maxPrice} className="w-full accent-brand-pink"
            onChange={(e) => setFilters({ ...filters, maxPrice: Math.max(Number(e.target.value), minPrice) })} />
        </label>
      </div>

      <Chips title="Store" options={facets.platforms} chosen={filters.selected} onToggle={toggle('selected')}
        dot={(p) => STORE_DOT[p] ?? '#999'} empty="All stores" />
      <Chips title="Category" options={facets.categories} chosen={filters.categories} onToggle={toggle('categories')} />
      <Chips title="Colour" options={facets.colours} chosen={filters.colours} onToggle={toggle('colours')}
        dot={(c) => COLOUR_DOT[c] ?? '#999'} />
      <Chips title="For" options={facets.genders} chosen={filters.genders} onToggle={toggle('genders')} />
      <Chips title="Occasion" options={facets.usages} chosen={filters.usages} onToggle={toggle('usages')} />
    </aside>
  )
}
