export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export type FlowVariant = "with_sow" | "without_sow";
export interface ProcessPhase { id:string; phase:string; process:string; time_minutes:number|null; owner:string; tools:string[]; actions:string[]; automation_tags:string[] }
export interface AutomationOpportunity { id:string; title:string; area:string; pain_point:string; automation:string; impact:string; complexity:string; estimated_saving_days_per_job:number }
export interface Summary { project:string; goal:string; variants:Record<FlowVariant,{phase_count:number;total_minutes:number;total_hours:number}>; automation_opportunity_count:number; top_pain_points:string[] }
export interface SavingsResponse { jobs_per_month:number; coverage_percent:number; baseline_days_saved_per_job:number; adjusted_days_saved_per_job:number; monthly_hours_saved:number; monthly_cost_saving:number; yearly_cost_saving:number }
async function request<T>(path:string, options?:RequestInit):Promise<T>{
  const res=await fetch(`${API_BASE}${path}`,{headers:{"Content-Type":"application/json",...(options?.headers||{})},...options});
  if(!res.ok) throw new Error(await res.text() || `Request failed ${res.status}`);
  return res.json();
}
export const api={
  summary:()=>request<Summary>("/api/summary"),
  flow:(v:FlowVariant)=>request<ProcessPhase[]>(`/api/flows/${v}`),
  opportunities:()=>request<AutomationOpportunity[]>("/api/automation-opportunities"),
  savings:(payload:{jobs_per_month:number;automation_coverage_percent:number;hourly_rate:number;hours_per_workday:number})=>request<SavingsResponse>("/api/savings",{method:"POST",body:JSON.stringify(payload)})
};
