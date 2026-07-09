import { LucideIcon } from "lucide-react";
export function StatCard({title,value,subtitle,icon:Icon}:{title:string;value:string;subtitle:string;icon:LucideIcon}) {
  return <div className="rounded-2xl border border-line bg-panel/80 p-5 shadow-2xl shadow-black/20">
    <div className="mb-4 flex items-center justify-between">
      <p className="text-sm text-zinc-400">{title}</p>
      <div className="rounded-xl bg-accent/15 p-2 text-accent"><Icon size={18}/></div>
    </div>
    <div className="text-3xl font-semibold text-white">{value}</div>
    <p className="mt-2 text-sm text-zinc-500">{subtitle}</p>
  </div>
}
