import { useCallback, useEffect, useState } from 'react'

const KEY = 'stylescout.wishlist.v1'

function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '[]')
    return Array.isArray(raw) ? raw : []
  } catch {
    return [] // storage blocked or corrupt: start empty, the app still works
  }
}

/** Saved items live in this browser only (localStorage). We store the whole product so the
 *  Saved page works without running a search again. */
export function useWishlist() {
  const [items, setItems] = useState(load)

  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify(items)) } catch { /* ignore */ }
  }, [items])

  const toggle = useCallback((product) => {
    setItems((list) => (list.some((p) => p.id === product.id)
      ? list.filter((p) => p.id !== product.id)
      : [product, ...list]))
  }, [])
  const clear = useCallback(() => setItems([]), [])

  return { items, ids: items.map((p) => p.id), toggle, clear }
}
