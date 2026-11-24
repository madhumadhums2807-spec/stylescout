import UploadZone from '../components/UploadZone'
import Loader from '../components/Loader'

const STEPS = [
  ['1', 'Upload a photo', 'Any dress, top, shoes or bag you like.'],
  ['2', 'We find lookalikes', 'AI compares it with thousands of styles.'],
  ['3', 'Shop in one tap', 'Open the store search or compare prices.'],
]
const CHIPS = ['Dresses', 'Kurtas', 'Sarees', 'Sneakers', 'Jackets']

// Decorative preview cards: real catalogue images served by the backend (hidden if one fails to load).
const PREVIEWS = [
  { src: '/images/2708.jpg', pct: 96, cls: 'left-[4%] top-8 -rotate-[7deg]' },
  { src: '/images/34302.jpg', pct: 94, cls: 'left-[31%] top-0 rotate-[3deg] z-10' },
  { src: '/images/1528.jpg', pct: 93, cls: 'left-[58%] top-12 rotate-[9deg]' },
]

export default function Home({ file, previewUrl, onSelect, onClear, onSearch, loading, error }) {
  return (
    <div className="relative overflow-hidden bg-[#171a2b] text-white">
      {/* soft colour glows */}
      <div className="pointer-events-none absolute -left-32 -top-24 h-[28rem] w-[28rem] rounded-full bg-brand-pink/50 blur-[110px]" aria-hidden="true" />
      <div className="pointer-events-none absolute -bottom-40 right-0 h-[26rem] w-[26rem] rounded-full bg-brand-orange/40 blur-[110px]" aria-hidden="true" />

      <section className="relative mx-auto grid max-w-6xl items-center gap-10 px-4 pb-12 pt-12 lg:grid-cols-2 lg:pb-16 lg:pt-16">
        <div className="text-center lg:text-left">
          <p className="pill bg-white/15 uppercase tracking-wider">AI fashion search</p>
          <h1 className="mt-5 font-display text-4xl font-extrabold leading-tight sm:text-5xl lg:text-[3.4rem]">
            Your next outfit,<br />
            <span className="bg-gradient-to-r from-brand-pink via-brand-orange to-brand-gold bg-clip-text text-transparent">found in a photo.</span>
          </h1>
          <p className="mx-auto mt-4 max-w-md text-base text-white/75 sm:text-lg lg:mx-0">
            Upload any look. StyleScout finds similar styles, lets you filter by budget and takes you straight to the store.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2 lg:justify-start" aria-hidden="true">
            {CHIPS.map((c) => (
              <span key={c} className="rounded-full border border-white/25 px-4 py-1.5 text-sm text-white/80">{c}</span>
            ))}
          </div>
          <ul className="mt-6 flex flex-wrap justify-center gap-x-5 gap-y-1 text-sm text-white/70 lg:justify-start">
            <li>&#10003; Match scores</li><li>&#10003; Budget &amp; colour filters</li><li>&#10003; Compare &amp; save</li>
          </ul>
        </div>

        <div>
          {/* floating match cards (desktop only, purely decorative) */}
          <div className="relative -mb-10 hidden h-64 lg:block" aria-hidden="true">
            {PREVIEWS.map((p) => (
              <div key={p.src} className={`absolute w-[34%] rounded-2xl bg-white p-2 shadow-[0_30px_70px_rgba(0,0,0,.45)] ${p.cls}`}>
                <img src={p.src} alt="" onError={(e) => { e.currentTarget.parentElement.style.display = 'none' }}
                  className="aspect-[3/4] w-full rounded-xl object-contain" />
                <p className="mt-1 text-sm font-bold text-brand-teal">{p.pct}% match</p>
              </div>
            ))}
          </div>

          <div className="relative z-20 rounded-3xl bg-white p-5 text-brand-plum shadow-lift sm:p-7">
            {loading ? (
              <Loader />
            ) : (
              <>
                <UploadZone file={file} previewUrl={previewUrl} onSelect={onSelect} onClear={onClear} />
                {file && (
                  <div className="mt-6 text-center">
                    <button className="btn btn-primary !px-10 !py-3.5 text-base" onClick={onSearch}>Find similar styles</button>
                  </div>
                )}
              </>
            )}
            {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-medium text-red-800">{error}</p>}
          </div>
        </div>
      </section>

      <section className="relative mx-auto grid max-w-4xl gap-4 px-4 pb-14 sm:grid-cols-3" aria-label="How it works">
        {STEPS.map(([n, title, text]) => (
          <div key={n} className="rounded-2xl border border-white/10 bg-white/10 p-5 backdrop-blur">
            <span className="mb-3 grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-brand-pink to-brand-orange font-display font-bold text-white">{n}</span>
            <h2 className="font-display text-base font-bold">{title}</h2>
            <p className="mt-1 text-sm text-white/70">{text}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
