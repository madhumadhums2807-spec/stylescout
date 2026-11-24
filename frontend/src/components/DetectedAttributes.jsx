const pct = (c) => `${Math.round(c * 100)}%`

/** Shows what the AI thinks the uploaded photo is. Worded as "detected", never as fact. */
export default function DetectedAttributes({ attributes, dominant, embedder }) {
  const chips = [
    ['Category', attributes.category, 'bg-brand-pink/10 text-brand-pink'],
    ['Colour', attributes.colour, 'bg-brand-orange/15 text-orange-700'],
  ].filter(([, a]) => a)

  return (
    <div className="rounded-2xl bg-white p-4 shadow-card">
      <h2 className="mb-2 font-display text-lg font-bold">What we detected</h2>
      <div className="flex flex-wrap items-center gap-2">
        {chips.map(([name, a, cls]) => (
          <span key={name} className={`pill ${cls}`}>
            {name}: <strong className="capitalize">{a.label}</strong> <span className="font-medium opacity-70">({pct(a.confidence)})</span>
          </span>
        ))}
        <span className="pill bg-brand-plum/5 text-brand-plum">
          <span className="h-3 w-3 rounded-full border border-brand-plum/20" style={{ background: dominant.hex }} />
          Dominant: <strong className="capitalize">{dominant.name}</strong>
        </span>
      </div>
      <p className="mt-2 text-xs text-brand-plum/50">
        Automatic guesses, they can be wrong. Method: {attributes.method}. Model: {embedder}.
      </p>
    </div>
  )
}
