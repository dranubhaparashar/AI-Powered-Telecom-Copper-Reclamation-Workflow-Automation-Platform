import { FlowVariant } from "../lib/api";
export function VariantToggle({value,onChange}:{value:FlowVariant;onChange:(v:FlowVariant)=>void}) {
  const items = [{label:"Without SOW",value:"without_sow" as FlowVariant},{label:"With SOW",value:"with_sow" as FlowVariant}];
  return <div className="inline-flex rounded-2xl border border-line bg-panel p-1">
    {items.map(i => <button key={i.value} onClick={()=>onChange(i.value)}
      className={["rounded-xl px-4 py-2 text-sm font-medium transition", value===i.value ? "bg-accent text-white shadow-lg shadow-accent/20" : "text-zinc-400 hover:bg-white/5 hover:text-white"].join(" ")}>
      {i.label}
    </button>)}
  </div>
}
