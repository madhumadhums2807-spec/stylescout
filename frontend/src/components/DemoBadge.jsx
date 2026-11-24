export function DemoBadge({ className = '' }) {
  return (
    <span className={`rounded-md bg-brand-plum/85 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white ${className}`}>
      Demo listing
    </span>
  )
}

export function DemoBanner() {
  return (
    <div role="note" className="bg-brand-plum px-4 py-1.5 text-center text-xs text-white/90">
      <strong className="text-brand-gold">Demo data:</strong> products are sample listings. Prices are placeholders; shop links open each store's search for the item.
    </div>
  )
}
