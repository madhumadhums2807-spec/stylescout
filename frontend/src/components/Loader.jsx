export default function Loader({ label = 'Finding similar styles...' }) {
  return (
    <div role="status" className="flex flex-col items-center gap-4 py-14 text-brand-plum/80">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-brand-pink/20 border-t-brand-pink" />
      <p className="text-sm font-medium">{label}</p>
      <div className="grid w-full max-w-md grid-cols-3 gap-3" aria-hidden="true">
        {[0, 1, 2].map((i) => <div key={i} className="aspect-[3/4] animate-pulse rounded-xl bg-brand-pink/10" />)}
      </div>
    </div>
  )
}
