/** Filter helpers shared by the app: default filter state, facet counts and the filter predicate. */
export const EMPTY_FILTERS = { selected: [], categories: [], colours: [], genders: [], usages: [], sort: 'match' }
const HIDDEN = new Set(['', 'na', 'n/a', 'none', 'null'])

export function defaultFilters(results) {
  const prices = results.map((p) => p.price)
  return {
    ...EMPTY_FILTERS,
    minPrice: Math.floor(Math.min(...prices) / 50) * 50,
    maxPrice: Math.ceil(Math.max(...prices) / 50) * 50,
  }
}

/** Count how many results have each value of a field, most common first. */
export function countBy(results, field) {
  const counts = new Map()
  for (const p of results) {
    const v = p[field]
    if (v == null || HIDDEN.has(String(v).trim().toLowerCase())) continue
    counts.set(v, (counts.get(v) ?? 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([value, count]) => ({ value, count }))
}

const pass = (chosen, value) => chosen.length === 0 || chosen.includes(value)

export function applyFilters(results, f) {
  return results.filter((p) =>
    p.price >= f.minPrice && p.price <= f.maxPrice &&
    pass(f.selected, p.platform) && pass(f.categories, p.category) &&
    pass(f.colours, p.color) && pass(f.genders, p.gender) && pass(f.usages, p.usage))
}

export function activeFilterCount(f, bounds) {
  return f.selected.length + f.categories.length + f.colours.length + f.genders.length + f.usages.length +
    (f.minPrice > bounds[0] || f.maxPrice < bounds[1] ? 1 : 0)
}

export const SORTERS = {
  match: (a, b) => b.score - a.score,
  price_asc: (a, b) => a.price - b.price,
  price_desc: (a, b) => b.price - a.price,
}
