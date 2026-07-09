import { motion } from "framer-motion";
import { ProcessPhase } from "../lib/api";
export function PhaseTimeline({phases,selectedId,onSelect}:{phases:ProcessPhase[];selectedId:string|null;onSelect:(id:string)=>void}) {
  return <div className="rounded-2xl border border-line bg-panel/80 p-5">
    <h2 className="text-lg font-semibold">Workflow Timeline</h2>
    <p className="mb-4 text-sm text-zinc-500">Click a phase to view details.</p>
    <div className="grid gap-3">{phases.map((p,i)=>{
      const active = selectedId === p.id;
      return <motion.button key={p.id} initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} transition={{delay:i*.04}}
        onClick={()=>onSelect(p.id)}
        className={["flex w-full items-start gap-4 rounded-2xl border p-4 text-left transition", active ? "border-accent bg-accent/10" : "border-line bg-panel2/60 hover:border-zinc-600 hover:bg-white/5"].join(" ")}>
        <div className={["flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold", active ? "bg-accent text-white" : "bg-zinc-800 text-zinc-300"].join(" ")}>{i+1}</div>
        <div>
          <div className="flex flex-wrap items-center gap-2"><h3 className="font-semibold text-white">{p.phase}</h3><span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">{p.time_minutes?`${p.time_minutes} min`:"Varies"}</span></div>
          <p className="mt-1 text-sm text-zinc-400">{p.process}</p>
          <p className="mt-2 text-xs uppercase tracking-wide text-zinc-500">{p.owner}</p>
        </div>
      </motion.button>
    })}</div>
  </div>
}
