export default function MetricCard({ title, value }) {
  return (
    <article className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4 shadow-lg shadow-black/30">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <p className="mt-2 text-xl font-semibold text-slate-100">{value}</p>
    </article>
  )
}
