import { useMemo, useState } from 'react'
import FilterPanel from '../components/FilterPanel'
import ProductCard from '../components/ProductCard'
import DetectedAttributes from '../components/DetectedAttributes'
import { SORTERS, activeFilterCount, applyFilters, countBy, defaultFilters } from '../services/facets'

const MAX_COMPARE = 4

/** Filtering happens HERE, in the browser, on the results we already fetched:
 *  moving a slider is instant and never re-runs the AI. */
export default function Results({ onShop, result, previewUrl, filters, setFilters, priceBounds, compareIds, onToggleCompare, onNewSearch, savedIds, onToggleSaved }) {
  const [showAnyway, setShowAnyway] = useState(false)
  const notFashion = result.looks_like_fashion === false && !showAnyway

  const facets = useMemo(() => ({
    platforms: countBy(result.results, 'platform'),
    categories: countBy(result.results, 'category'),
    colours: countBy(result.results, 'color'),
    genders: countBy(result.results, 'gender'),
    usages: countBy(result.results, 'usage'),
  }), [result])

  const visible = useMemo(
    () => [...applyFilters(result.results, filters)].sort(SORTERS[filters.sort]),
    [result, filters])
  const activeCount = activeFilterCount(filters, priceBounds)
  const clearFilters = () => setFilters({ ...defaultFilters(result.results), sort: filters.sort })
  const panelProps = { filters, setFilters, facets, priceBounds, resultCount: visible.length,
    totalCount: result.results.length, activeCount, onClear: clearFilters }

  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 grid gap-4 md:grid-cols-[160px_1fr]">
        <img src={previewUrl} alt="Your photo" className="h-40 w-40 rounded-2xl border-4 border-white bg-white object-contain shadow-card" />
        <div className="space-y-3">
          {notFashion ? (
            <div role="alert" className="rounded-2xl border-2 border-brand-gold bg-amber-50 p-4 text-sm text-amber-900">
              <p className="font-medium">This doesn't look like a clothing or footwear photo.</p>
              <p className="mt-1">StyleScout is built for fashion items, so these matches would not be meaningful.
                Try a photo of a dress, shirt, shoes or a bag.</p>
              <button className="btn btn-ghost mt-3 !py-1.5" onClick={() => setShowAnyway(true)}>Show the closest products anyway</button>
            </div>
          ) : (
            <DetectedAttributes attributes={result.attributes} dominant={result.dominant_colour} embedder={result.embedder} />
          )}
          <button className="btn btn-ghost" onClick={onNewSearch}>New search</button>
        </div>
      </div>

      {!notFashion && (
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <div className="lg:sticky lg:top-20 lg:self-start">
          {/* phones: collapsible; desktop: always open in the side column */}
          <details className="rounded-2xl bg-white shadow-card lg:hidden">
            <summary className="cursor-pointer list-none px-5 py-3 font-display font-bold text-brand-pink">
              Filters{activeCount > 0 && ` (${activeCount})`} <span className="font-sans text-sm font-normal text-brand-plum/50">({visible.length} shown)</span>
            </summary>
            <FilterPanel {...panelProps} />
          </details>
          <div className="hidden lg:block">
            <FilterPanel {...panelProps} />
          </div>
        </div>
        <div>
          {visible.length === 0 ? (
            <p className="rounded-2xl border-2 border-dashed border-brand-pink/30 bg-white p-10 text-center text-brand-plum/70">
              No products match these filters. Try widening the budget or removing a filter.
              <button className="btn btn-primary mt-4 block mx-auto" onClick={clearFilters}>Clear all filters</button>
            </p>
          ) : (
            <>
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <h2 className="font-display text-xl font-bold">Similar styles for you <span className="text-brand-plum/40">({visible.length})</span></h2>
                <label className="flex items-center gap-2 text-sm font-medium text-brand-plum/70">Sort by
                  <select value={filters.sort} onChange={(e) => setFilters({ ...filters, sort: e.target.value })}
                    className="rounded-full border-2 border-brand-plum/15 bg-white px-3 py-1.5 text-sm font-bold text-brand-plum focus:border-brand-pink focus:outline-none">
                    <option value="match">Best match</option>
                    <option value="price_asc">Price: low to high</option>
                    <option value="price_desc">Price: high to low</option>
                  </select>
                </label>
              </div>
            <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3">
              {visible.map((p) => (
                <ProductCard key={p.id} product={p} selected={compareIds.includes(p.id)}
                  compareDisabled={compareIds.length >= MAX_COMPARE} onToggleCompare={onToggleCompare} onShop={onShop}
                  saved={savedIds.includes(p.id)} onToggleSaved={onToggleSaved} />
              ))}
            </div>
            </>
          )}
        </div>
      </div>
      )}
    </section>
  )
}
