import { ProcessPhase } from "../lib/api";
import { CheckCircle2, Wrench } from "lucide-react";
export function PhaseDetail({phase}:{phase?:ProcessPhase}) {
  if(!phase) return <div className="rounded-2xl border border-line bg-panel/80 p-6 text-zinc-400">Select a phase.</div>;
  return <div className="rounded-2xl border border-line bg-panel/80 p-6">
    <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
      <div><p className="text-sm text-accent">{phase.owner}</p><h2 className="mt-1 text-2xl font-semibold">{phase.phase}</h2><p className="mt-2 max-w-2xl text-zinc-400">{phase.process}</p></div>
      <div className="rounded-2xl border border-line bg-panel2 px-4 py-3 text-right"><p className="text-xs text-zinc-500">Estimated Time</p><p className="text-xl font-semibold">{phase.time_minutes?`${phase.time_minutes} min`:"Varies"}</p></div>
    </div>
    <div className="grid gap-5 lg:grid-cols-2">
      <section><div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-300"><CheckCircle2 size={18} className="text-accent"/>Process Actions</div><div className="space-y-2">{phase.actions.map(a=><div key={a} className="rounded-xl border border-line bg-ink/40 p-3 text-sm text-zinc-300">{a}</div>)}</div></section>
      <section><div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-300"><Wrench size={18} className="text-accent"/>Tools & Automation Tags</div><div className="mb-4 flex flex-wrap gap-2">{phase.tools.map(t=><span key={t} className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-300">{t}</span>)}</div><div className="flex flex-wrap gap-2">{phase.automation_tags.map(t=><span key={t} className="rounded-full bg-accent/15 px-3 py-1 text-xs text-accent">#{t}</span>)}</div></section>
    </div>
  </div>
}
