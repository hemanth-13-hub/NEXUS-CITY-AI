from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import Report, ReportHistory
from .services.ai_service import analyze

SAMPLES = [
("Water pipe leak by residential lane","Water has been leaking from a damaged pipe since morning near the residential lane.","Water Leakage","Sample Zone A",17.3850,78.4867,"Reported",3),
("Waterlogging after heavy rain","Rainwater is standing across the service road and slowing traffic.","Waterlogging","Sample Zone B",17.3910,78.4800,"Under Review",2),
("Large pothole near bus stop","A large pothole is damaging vehicles near the bus stop.","Potholes","Sample Zone C",17.3780,78.4920,"In Progress",5),
("Blocked drainage outlet","The drain is blocked and wastewater is overflowing onto the footpath.","Blocked Drainage","Sample Zone D",17.4000,78.4700,"Reported",1),
("Streetlight not working","The streetlight has stopped working on a residential street.","Streetlight Failure","Sample Zone E",17.3700,78.5000,"Resolved",12),
("Cracked road surface","Road surface is cracked near the public building entrance.","Road Damage","Sample Zone F",17.4100,78.4900,"Under Review",4),
("Suspected slope movement","Residents noticed soil movement on a hillside after rainfall; inspection is needed.","Landslide Risk","Sample Zone G",17.4200,78.4600,"Reported",1),
("Overflowing storm drain","Water is overflowing from a storm drain onto the road.","Flooding","Sample Zone H",17.3600,78.4750,"In Progress",8),
("Damaged pavement","The pavement is broken and needs inspection.","Road Damage","Sample Zone I",17.3950,78.5050,"Resolved",15),
("Tap leak at community area","A public water tap is leaking and wasting water.","Water Leakage","Sample Zone J",17.3820,78.4650,"Reported",0),
]

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Report).where(Report.public_report_id.like("DEMO-%"))):
            print("Sample data already exists; no changes made."); return
        now=datetime.now(timezone.utc)
        for i,(title,desc,cat,loc,lat,lon,status,age) in enumerate(SAMPLES,1):
            a=analyze(title,desc,cat); created=now-timedelta(days=age)
            r=Report(public_report_id=f"DEMO-{i:04d}",title=title,description=desc,citizen_category=cat,ai_suggested_category=a['suggested_category'],location_name=loc,latitude=lat,longitude=lon,severity=a['severity'],ai_explanation=a['explanation'],ai_summary=a['summary'],department=a['department'],status=status,created_at=created,updated_at=created,resolved_at=created+timedelta(hours=8) if status=="Resolved" else None)
            db.add(r); db.flush(); db.add(ReportHistory(report_id=r.id,previous_status=None,new_status="Reported",changed_by="Seed script",change_note="Fictional demonstration record"))
            if status != "Reported": db.add(ReportHistory(report_id=r.id,previous_status="Reported",new_status=status,changed_by="Seed script",change_note="Fictional demonstration record"))
        db.commit(); print(f"Inserted {len(SAMPLES)} fictional demonstration reports.")
if __name__ == "__main__": seed()
