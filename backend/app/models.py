from typing import List, Optional
from pydantic import BaseModel, Field

class ProcessPhase(BaseModel):
    id: str
    phase: str
    process: str
    time_minutes: Optional[float]
    owner: str
    tools: List[str]
    actions: List[str]
    automation_tags: List[str]

class AutomationOpportunity(BaseModel):
    id: str
    title: str
    area: str
    pain_point: str
    automation: str
    impact: str
    complexity: str
    estimated_saving_days_per_job: float

class SavingsRequest(BaseModel):
    jobs_per_month: int = Field(default=10, ge=1, le=1000)
    automation_coverage_percent: float = Field(default=60, ge=0, le=100)
    hourly_rate: float = Field(default=45, ge=0)
    hours_per_workday: float = Field(default=8, gt=0, le=24)
