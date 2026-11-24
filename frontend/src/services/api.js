// All HTTP calls live here, so components never build URLs or parse errors themselves.

async function handle(res) {
  if (res.ok) return res.json()
  let detail = `Request failed (${res.status})`
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') detail = body.detail
    else if (Array.isArray(body.detail)) detail = body.detail.map((d) => d.msg).join('; ')
  } catch { /* body was not JSON */ }
  throw new Error(detail)
}

/** Upload an image. Filters are optional: the UI usually searches unfiltered and filters locally. */
export async function searchByImage(file, { minPrice, maxPrice, platforms, sort, topK } = {}) {
  const form = new FormData()
  form.append('file', file)
  if (minPrice != null) form.append('min_price', minPrice)
  if (maxPrice != null) form.append('max_price', maxPrice)
  if (platforms?.length) form.append('platforms', platforms.join(','))
  if (sort) form.append('sort', sort)
  if (topK) form.append('top_k', topK)
  return handle(await fetch('/api/search', { method: 'POST', body: form }))
}

export async function compareProducts(ids) {
  return handle(
    await fetch('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids }),
    }),
  )
}

export const getPlatforms = async () => handle(await fetch('/api/platforms'))
export const getHealth = async () => handle(await fetch('/api/health'))

/** More products like this one (same category), nearest first. */
export const getSimilar = async (id, limit = 12) => handle(await fetch(`/api/products/${id}/similar?limit=${limit}`))
