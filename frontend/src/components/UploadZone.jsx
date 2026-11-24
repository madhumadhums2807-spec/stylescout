import { useRef, useState } from 'react'

const ALLOWED = ['image/jpeg', 'image/png', 'image/webp']
const MAX_MB = 5

/** Drag-and-drop / tap-to-choose uploader with a live preview and client-side checks.
 *  (The server re-validates everything: client checks are only for fast feedback.) */
export default function UploadZone({ file, previewUrl, onSelect, onClear, disabled }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')

  function accept(f) {
    if (!f) return
    if (!ALLOWED.includes(f.type)) return setError('Please choose a JPG, PNG or WEBP image.')
    if (f.size > MAX_MB * 1024 * 1024) return setError(`Image must be smaller than ${MAX_MB} MB.`)
    setError('')
    onSelect(f)
  }

  if (file) {
    return (
      <div className="flex flex-col items-center gap-4">
        <img src={previewUrl} alt="Your uploaded outfit" className="max-h-72 rounded-2xl border-4 border-white bg-white object-contain shadow-card" />
        <p className="max-w-full truncate text-sm text-brand-plum/60">{file.name}</p>
        <button className="btn btn-ghost" onClick={onClear} disabled={disabled}>Choose a different photo</button>
      </div>
    )
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); accept(e.dataTransfer.files?.[0]) }}
        className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${
          dragging ? 'border-brand-pink bg-brand-pink/10' : 'border-brand-pink/40 bg-brand-mist hover:border-brand-pink hover:bg-brand-pink/5'
        }`}
      >
        <span className="grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br from-brand-pink to-brand-orange text-white shadow-lift floaty" aria-hidden="true">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" />
          </svg>
        </span>
        <p className="font-display text-lg font-bold">Tap to upload or take a photo</p>
        <p className="text-sm text-brand-plum/60">or drag and drop here. JPG, PNG or WEBP, up to {MAX_MB} MB</p>
        <input ref={inputRef} type="file" accept=".jpg,.jpeg,.png,.webp" className="hidden" onChange={(e) => accept(e.target.files?.[0])} />
      </div>
      {error && <p role="alert" className="mt-3 text-sm font-medium text-red-700">{error}</p>}
    </div>
  )
}
