from datetime import datetime, timezone
import hashlib
import json
from uuid import UUID, uuid4
from ..config import APP_ENV, UPLOAD_DIR
from fastapi import APIRouter, Depends, Header, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Report, ReportHistory
from ..schemas import ReportCreate, ReportOut, ReportUpdate, HistoryOut, CATEGORIES
from ..services.ai_service import analyze

router = APIRouter(prefix="/api/reports", tags=["reports"])


def require_development_admin():
    if APP_ENV == "production":
        raise HTTPException(
            status_code=404,
            detail="Operations endpoints are disabled until authentication is configured",
        )


def get_report(db: Session, report_id: str):
    q = select(Report).options(selectinload(Report.history)).where(Report.public_report_id == report_id)
    report = db.scalar(q)
    if not report:
        try: report = db.get(Report, int(report_id))
        except (ValueError, TypeError): pass
    if not report: raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("", response_model=ReportOut, status_code=201)
def create_report(
    payload: ReportCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    payload_json = json.dumps(
        payload.model_dump(), sort_keys=True, separators=(",", ":")
    )
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    if idempotency_key is not None:
        try:
            idempotency_key = str(UUID(idempotency_key))
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="Idempotency-Key must be a valid UUID"
            ) from exc
        existing = db.scalar(
            select(Report).where(Report.idempotency_key == idempotency_key)
        )
        if existing:
            if existing.idempotency_payload_hash != payload_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency-Key was already used for a different report",
                )
            return existing
    analysis = analyze(payload.title, payload.description, payload.citizen_category)
    report = Report(public_report_id=f"NX-{uuid4().hex[:8].upper()}", **payload.model_dump(),
                    ai_suggested_category=analysis["suggested_category"], severity=analysis["severity"],
                    ai_explanation=analysis["explanation"], ai_summary=analysis["summary"], department=analysis["department"])
    report.idempotency_key = idempotency_key
    report.idempotency_payload_hash = payload_hash if idempotency_key else None
    db.add(report)
    try:
        db.flush()
        db.add(ReportHistory(report_id=report.id, previous_status=None, new_status="Reported", changed_by="Citizen", change_note="Report submitted"))
        db.commit()
    except IntegrityError:
        db.rollback()
        if idempotency_key is None:
            raise
        existing = db.scalar(
            select(Report).where(Report.idempotency_key == idempotency_key)
        )
        if not existing:
            raise
        if existing.idempotency_payload_hash != payload_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key was already used for a different report",
            )
        return existing
    db.refresh(report)
    return report

@router.get("", response_model=list[ReportOut])
def list_reports(status: str | None = None, category: str | None = None, severity: str | None = None,
                 q: str | None = Query(default=None, max_length=140), limit: int = Query(default=100, ge=1, le=500),
                 offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    stmt = select(Report).order_by(Report.created_at.desc()).offset(offset).limit(limit)
    if status: stmt = stmt.where(Report.status == status)
    if category: stmt = stmt.where(Report.citizen_category == category)
    if severity: stmt = stmt.where(Report.severity == severity)
    if q: stmt = stmt.where((Report.title.ilike(f"%{q}%")) | (Report.public_report_id.ilike(f"%{q}%")) | (Report.location_name.ilike(f"%{q}%")))
    return list(db.scalars(stmt).all())

@router.get("/{report_id}", response_model=ReportOut)
def report_detail(report_id: str, db: Session = Depends(get_db)):
    return get_report(db, report_id)

@router.get("/{report_id}/history", response_model=list[HistoryOut])
def report_history(report_id: str, db: Session = Depends(get_db)):
    report = get_report(db, report_id)
    return list(db.scalars(select(ReportHistory).where(ReportHistory.report_id == report.id).order_by(ReportHistory.created_at)).all())

@router.patch("/{report_id}", response_model=ReportOut)
def update_report(report_id: str, payload: ReportUpdate, db: Session = Depends(get_db)):
    require_development_admin()
    report = get_report(db, report_id); data = payload.model_dump(exclude_unset=True)
    note = data.pop("change_note", None); previous = report.status
    for key, value in data.items():
        if value is not None: setattr(report, key, value)
    if report.status != previous:
        if report.status == "Resolved": report.resolved_at = datetime.now(timezone.utc)
        else: report.resolved_at = None
        db.add(ReportHistory(report_id=report.id, previous_status=previous, new_status=report.status, change_note=note, changed_by="Development admin"))
    report.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(report)
    return report

@router.post("/{report_id}/analyze", response_model=ReportOut)
def reanalyze_report(report_id: str, db: Session = Depends(get_db)):
    require_development_admin()
    report = get_report(db, report_id); a = analyze(report.title, report.description, report.citizen_category)
    report.ai_suggested_category = a["suggested_category"]; report.ai_summary = a["summary"]; report.ai_explanation = a["explanation"]
    report.severity = a["severity"]; report.department = a["department"]; db.commit(); db.refresh(report)
    return report


@router.post("/{report_id}/image", response_model=ReportOut)
async def upload_report_image(report_id: str, image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Development upload endpoint; validates file signature and limits size to 5 MiB."""
    require_development_admin()
    report = get_report(db, report_id)
    allowed = {"image/jpeg": (".jpg", (b"\xff\xd8\xff",)), "image/png": (".png", (b"\x89PNG\r\n\x1a\n",)), "image/webp": (".webp", (b"RIFF",)), "image/gif": (".gif", (b"GIF87a", b"GIF89a"))}
    if image.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, WEBP, or GIF image")
    data = await image.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 5 MiB or smaller")
    ext, signatures = allowed[image.content_type]
    valid = any(data.startswith(sig) for sig in signatures)
    if image.content_type == "image/webp": valid = data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    if not valid:
        raise HTTPException(status_code=415, detail="Image content does not match its declared file type")
    filename = f"{report.public_report_id}{ext.lower()}"
    (UPLOAD_DIR / filename).write_bytes(data)
    report.image_path = f"/uploads/{filename}"
    report.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(report)
    return report
