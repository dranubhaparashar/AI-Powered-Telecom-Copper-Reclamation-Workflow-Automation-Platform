import { useEffect, useMemo, useState } from "react";
import { Activity, Clock3, FileText, Sparkles } from "lucide-react";
import { api, AutomationOpportunity, FlowVariant, ProcessPhase, Summary } from "./lib/api";
import { StatCard } from "./components/StatCard";
import { VariantToggle } from "./components/VariantToggle";
import { PhaseTimeline } from "./components/PhaseTimeline";
import { PhaseDetail } from "./components/PhaseDetail";
import { AutomationBacklog } from "./components/AutomationBacklog";
import { SavingsCalculator } from "./components/SavingsCalculator";

function App() {
  const [variant,setVariant] = useState<FlowVariant>("without_sow");
  const [summary,setSummary] = useState<Summary|null>(null);
  const [phases,setPhases] = useState<ProcessPhase[]>([]);
  const [opps,setOpps] = useState<AutomationOpportunity[]>([]);
  const [selectedId,setSelectedId] = useState<string|null>(null);
  const [error,setError] = useState<string|null>(null);

  useEffect(()=>{ Promise.all([api.summary(), api.opportunities()]).then(([s,o])=>{setSummary(s);setOpps(o)}).catch(e=>setError(e.message)) }, []);
  useEffect(()=>{ api.flow(variant).then(data=>{setPhases(data);setSelectedId(data[0]?.id ?? null)}).catch(e=>setError(e.message)) }, [variant]);

  const selected = useMemo(()=>phases.find(p=>p.id===selectedId), [phases,selectedId]);
  const totalMinutes = summary?.variants[variant].total_minutes ?? phases.reduce((a,p)=>a+(p.time_minutes||0),0);
  const totalHours = Math.round((totalMinutes/60)*10)/10;

  const exportReport = () => {
    const blob = new Blob([JSON.stringify({generated_at:new Date().toISOString(), selected_variant:variant, summary, phases, automation_opportunities:opps}, null, 2)], {type:"application/json"});
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = `reclamation-report-${variant}.json`;
    link.click();
    URL.revokeObjectURL(href);
  };

  return <main className="mx-auto max-w-7xl px-5 py-8">
    <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-sm text-accent"><Sparkles size={15}/>AT&T Network Design • Reclamation Automation</div>
        <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-white md:text-6xl">Reclamation AI Platform</h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-zinc-400">Workflow dashboard for copper decommissioning: compare With SOW vs Without SOW, inspect each phase, and prioritize automation candidates.</p>
      </div>
      <div className="flex flex-wrap gap-3"><VariantToggle value={variant} onChange={setVariant}/><button onClick={exportReport} className="rounded-2xl border border-line bg-panel px-4 py-2 text-sm font-medium text-zinc-200 hover:border-accent hover:text-white">Export JSON Report</button></div>
    </header>

    {error && <div className="mb-6 rounded-2xl border border-red-500/40 bg-red-500/10 p-4 text-red-200">API error: {error}. Start FastAPI on http://localhost:8000.</div>}

    <section className="mb-6 grid gap-4 md:grid-cols-4">
      <StatCard title="Selected Flow" value={variant==="with_sow"?"With SOW":"Without SOW"} subtitle="Workflow variant" icon={FileText}/>
      <StatCard title="Total Phases" value={`${phases.length}`} subtitle="Mapped process steps" icon={Activity}/>
      <StatCard title="Estimated Effort" value={`${totalHours}h`} subtitle={`${totalMinutes} minutes, excluding variable work`} icon={Clock3}/>
      <StatCard title="Automation Ideas" value={`${opps.length}`} subtitle="Prioritized backlog" icon={Sparkles}/>
    </section>

    <section className="mb-6 grid gap-6 lg:grid-cols-[0.95fr_1.4fr]">
      <PhaseTimeline phases={phases} selectedId={selectedId} onSelect={setSelectedId}/>
      <PhaseDetail phase={selected}/>
    </section>

    <section className="mb-6"><SavingsCalculator/></section>
    <section className="mb-10"><AutomationBacklog items={opps}/></section>
  </main>
}
export default App;
