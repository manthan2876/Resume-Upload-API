from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RecruiterDashboard, HiringManagerDashboard, TalentLeaderDashboard

router = APIRouter(prefix="/api/v1/analytics/dashboard", tags=["Analytics"])

@router.get("/recruiter", response_model=RecruiterDashboard)
async def get_recruiter_dashboard(db: Session = Depends(get_db)):
    return RecruiterDashboard(
        time_to_hire=24.5,
        time_to_fill=30.0,
        sourcing_channel_efficiency={
            "LinkedIn": 85.0,
            "Referrals": 92.0,
            "Indeed": 65.0
        },
        application_completion_rate=78.5,
        stage_drop_off={
            "Applied": 100,
            "Screened": 60,
            "Interview": 20,
            "Offer": 10,
            "Hired": 8
        },
        offer_acceptance_rate=80.0
    )

@router.get("/hiring-manager", response_model=HiringManagerDashboard)
async def get_hiring_manager_dashboard(db: Session = Depends(get_db)):
    return HiringManagerDashboard(
        quality_of_hire=88.5,
        interview_to_offer_ratio=3.5,
        candidates_in_progress={
            "Screened": 12,
            "Interviewing": 5,
            "Final Round": 2
        },
        early_turnover_rate=5.0
    )

@router.get("/talent-leader", response_model=TalentLeaderDashboard)
async def get_talent_leader_dashboard(db: Session = Depends(get_db)):
    return TalentLeaderDashboard(
        cost_per_hire=4500.0,
        recruitment_roi=3.2,
        diversity_metrics={
            "Gender": {"Male": 52, "Female": 45, "Non-binary": 3},
            "Ethnicity": {"Group A": 40, "Group B": 30, "Group C": 20, "Other": 10}
        },
        hiring_volume_vs_plan={
            "Target": 50,
            "Actual": 42,
            "Pipeline": 120
        }
    )
