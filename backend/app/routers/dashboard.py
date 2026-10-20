from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Report
from ..schemas import CATEGORIES, STATUSES, SEVERITIES

router = APIRouter(prefix="/api", tags=["dashboard"])

def all_reports(db): return list(db.scalars(select(Report).order_by(Report.created_at.asc())).all())

@router.get("/dashboard/summary")
def summary(db: Session = Depends(get_db)):
    rs = all_reports(db); counts = Counter(r.status for r in rs)
    return {"total":len(rs), "reported":counts["Reported"], "under_review":counts["Under Review"], "in_progress":counts["In Progress"], "resolved":counts["Resolved"], "high_open":sum(r.severity=="High" and r.status!="Resolved" for r in rs), "sample_data_included":any(r.public_report_id.startswith("DEMO-") for r in rs)}

@router.get("/dashboard/analytics")
def analytics(db: Session = Depends(get_db)):
    rs = all_reports(db); category=Counter(r.citizen_category for r in rs); status=Counter(r.status for r in rs); severity=Counter(r.severity for r in rs); department=Counter(r.department for r in rs if r.status!="Resolved")
    days=defaultdict(int)
    for r in rs: days[r.created_at.date().isoformat()] += 1
    trend = [{"date":(datetime.now(timezone.utc).date()-timedelta(days=i)).isoformat(),"count":days[(datetime.now(timezone.utc).date()-timedelta(days=i)).isoformat()]} for i in reversed(range(7))]
    durations=[(r.resolved_at-r.created_at).total_seconds()/3600 for r in rs if r.status=="Resolved" and r.resolved_at and r.created_at]
    return {"by_category":[{"name":k,"value":category[k]} for k in CATEGORIES if category[k]],"by_status":[{"name":k,"value":status[k]} for k in STATUSES],"by_severity":[{"name":k,"value":severity[k]} for k in SEVERITIES],"by_department":[{"name":k,"value":v} for k,v in department.items()],"trend":trend,"average_resolution_hours":round(sum(durations)/len(durations),1) if durations else None,"resolved_with_duration":len(durations)}

@router.get("/map/reports")
def map_reports(db: Session = Depends(get_db)):
    return [{"public_report_id":r.public_report_id,"title":r.title,"citizen_category":r.citizen_category,"severity":r.severity,"status":r.status,"location_name":r.location_name,"latitude":r.latitude,"longitude":r.longitude,"created_at":r.created_at} for r in all_reports(db) if r.latitude is not None and r.longitude is not None and -90 <= r.latitude <= 90 and -180 <= r.longitude <= 180]

@router.post("/track")
def track(payload: dict, db: Session = Depends(get_db)):
    report_id = str(payload.get("report_id", "")).strip()
    if not report_id: from fastapi import HTTPException; raise HTTPException(400, "Enter a report ID")
    report = db.scalar(select(Report).where(Report.public_report_id == report_id))
    if not report: from fastapi import HTTPException; raise HTTPException(404, "No report found for that ID")
    return {"public_report_id":report.public_report_id,"title":report.title,"citizen_category":report.citizen_category,"location_name":report.location_name,"status":report.status,"department":report.department,"created_at":report.created_at,"updated_at":report.updated_at,"resolved_at":report.resolved_at}
