// Builds "shop this" links.
//
// IMPORTANT (honesty): our catalogue is demo data, so we do not have real product-page URLs.
// Each link below opens the store's own SEARCH page for the product name. The shopper sees what the
// store really has; the price/stock there may differ from the sample price shown in StyleScout.
// Linking straight to a live product page needs a store's authorised product/affiliate API.

const enc = encodeURIComponent

export const STORES = {
  Myntra: { name: 'Myntra', bg: '#ff3f6c', fg: '#ffffff', url: (q) => `https://www.myntra.com/${q.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-')}` },
  Ajio: { name: 'Ajio', bg: '#2c4152', fg: '#ffffff', url: (q) => `https://www.ajio.com/search/?text=${enc(q)}` },
  Meesho: { name: 'Meesho', bg: '#9f2089', fg: '#ffffff', url: (q) => `https://www.meesho.com/search?q=${enc(q)}` },
  Flipkart: { name: 'Flipkart', bg: '#2874f0', fg: '#ffffff', url: (q) => `https://www.flipkart.com/search?q=${enc(q)}` },
  Amazon: { name: 'Amazon', bg: '#ffb100', fg: '#111111', url: (q) => `https://www.amazon.in/s?k=${enc(q)}` },
}

/** The store the sample listing is labelled with (falls back to Amazon if unknown). */
export function primaryStore(product, preferred) {
  const store = STORES[preferred] ?? STORES[product.platform] ?? STORES.Amazon
  return { ...store, href: store.url(product.name) }
}

/** Quick "also check" links on the big marketplaces. */
export function otherStores(product, primaryName) {
  return Object.keys(STORES)
    .filter((n) => n !== primaryName)
    .map((n) => ({ ...STORES[n], href: STORES[n].url(product.name) }))
}
