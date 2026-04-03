export default function ControlSlider({ label, value, min, max, step = 1, onChange }) {
  return (
    <label className="space-y-2">
      <div className="flex items-center justify-between text-sm text-slate-300">
        <span>{label}</span>
        <span className="rounded bg-slate-700/70 px-2 py-0.5 text-cyan-300">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-700 accent-cyan-400"
      />
    </label>
  )
}
