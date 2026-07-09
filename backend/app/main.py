import json
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ProcessPhase, AutomationOpportunity, SavingsRequest

DATA_DIR = Path(__file__).resolve().parent / "data"
app = FastAPI(title="Reclamation AI Platform API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_json(name: str):
    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"Missing data file: {name}")
    return json.loads(path.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "ok", "service": "Reclamation AI Platform API"}

@app.get("/api/flows")
def all_flows():
    return load_json("process_flows.json")

@app.get("/api/flows/{variant}", response_model=list[ProcessPhase])
def flow(variant: Literal["with_sow", "without_sow"]):
    return load_json("process_flows.json")[variant]

@app.get("/api/summary")
def summary():
    flows = load_json("process_flows.json")
    opps = load_json("automation_opportunities.json")
    def total(items):
        return sum((x.get("time_minutes") or 0) for x in items)
    return {
      "project": "AT&T Reclamation / Copper Decommissioning Workflow Automation",
      "goal": "Map the end-to-end reclamation workflow and identify automation opportunities that reduce manual effort, errors, and turnaround time.",
      "variants": {
        "without_sow": {"phase_count": len(flows["without_sow"]), "total_minutes": total(flows["without_sow"]), "total_hours": round(total(flows["without_sow"])/60, 2)},
        "with_sow": {"phase_count": len(flows["with_sow"]), "total_minutes": total(flows["with_sow"]), "total_hours": round(total(flows["with_sow"])/60, 2)}
      },
      "automation_opportunity_count": len(opps),
      "top_pain_points": ["Manual PTGUI/ICC report extraction", "Cross-system circuit validation", "Excel master-sheet creation", "Field data mismatch", "SOW/FID/LAT-LONG extraction", "Permit and gas pipeline checks"]
    }

@app.get("/api/automation-opportunities", response_model=list[AutomationOpportunity])
def automation_opportunities():
    return load_json("automation_opportunities.json")

@app.post("/api/savings")
def savings(payload: SavingsRequest):
    opps = load_json("automation_opportunities.json")
    baseline_days = sum(x["estimated_saving_days_per_job"] for x in opps)
    adjusted_days = baseline_days * (payload.automation_coverage_percent / 100)
    monthly_hours = adjusted_days * payload.jobs_per_month * payload.hours_per_workday
    monthly_cost = monthly_hours * payload.hourly_rate
    return {
      "jobs_per_month": payload.jobs_per_month,
      "coverage_percent": payload.automation_coverage_percent,
      "baseline_days_saved_per_job": round(baseline_days, 2),
      "adjusted_days_saved_per_job": round(adjusted_days, 2),
      "monthly_hours_saved": round(monthly_hours, 2),
      "monthly_cost_saving": round(monthly_cost, 2),
      "yearly_cost_saving": round(monthly_cost * 12, 2)
    }
