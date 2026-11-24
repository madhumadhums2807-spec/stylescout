import ProductCard from '../components/ProductCard'

export default function Saved({ items, onToggleSaved, onClear, onShop, onBack }) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">
          Saved items <span className="text-brand-plum/40">({items.length})</span>
        </h1>
        <div className="flex gap-2">
          {items.length > 0 && <button className="btn btn-ghost" onClick={onClear}>Clear all</button>}
          <button className="btn btn-primary" onClick={onBack}>Back to shopping</button>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="rounded-2xl border-2 border-dashed border-brand-pink/30 bg-white p-10 text-center text-brand-plum/70">
          Nothing saved yet. Tap the heart on any product to keep it here.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4">
          {items.map((p) => (
            <ProductCard key={p.id} product={p} saved onToggleSaved={onToggleSaved} onShop={onShop} />
          ))}
        </div>
      )}
      <p className="mt-6 text-center text-xs text-brand-plum/50">Saved items are stored in this browser only.</p>
    </section>
  )
}
