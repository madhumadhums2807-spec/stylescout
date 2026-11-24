export default function Navbar({ onHome, compareCount, onOpenCompare, savedCount, onOpenSaved }) {
  return (
    <header className="sticky top-0 z-30 bg-gradient-to-r from-brand-pink via-rose-500 to-brand-orange text-white shadow-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <button onClick={onHome} className="flex items-center gap-2" aria-label="StyleScout home">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-white/25 font-display text-lg font-extrabold">S</span>
          <span className="font-display text-2xl font-extrabold tracking-tight">StyleScout</span>
        </button>
        <div className="flex items-center gap-2">
        <button onClick={onOpenSaved} aria-label="Open saved items"
          className="relative inline-flex items-center gap-1.5 rounded-full bg-white/20 px-4 py-2 text-sm font-bold text-white transition hover:bg-white/30">
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.5-9.2C1 8.3 3 5 6.3 5c2 0 3.5 1.1 4.2 2.4h3C14.2 6.1 15.7 5 17.7 5 21 5 23 8.3 21.5 11.8 19.5 16.4 12 21 12 21z" /></svg>
          Saved
          {savedCount > 0 && <span className="grid h-5 min-w-[1.25rem] place-items-center rounded-full bg-white px-1 text-xs text-brand-pink">{savedCount}</span>}
        </button>
        <button onClick={onOpenCompare} aria-label="Open comparison"
          className="relative inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-bold text-brand-pink shadow transition hover:shadow-lg">
          Compare
          {compareCount > 0 && (
            <span className="grid h-5 min-w-[1.25rem] place-items-center rounded-full bg-brand-pink px-1 text-xs text-white">{compareCount}</span>
          )}
        </button>
        </div>
      </div>
    </header>
  )
}
