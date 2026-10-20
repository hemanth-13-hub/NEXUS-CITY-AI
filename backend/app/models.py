from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow(): return datetime.now(timezone.utc)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_report_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(140))
    description: Mapped[str] = mapped_column(Text)
    citizen_category: Mapped[str] = mapped_column(String(50), index=True)
    ai_suggested_category: Mapped[str] = mapped_column(String(50), default="Other Infrastructure Issues")
    location_name: Mapped[str] = mapped_column(String(220), default="Location not provided")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(12), default="Medium", index=True)
    ai_explanation: Mapped[str] = mapped_column(Text, default="Rule-based preliminary assessment")
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(String(80), default="General Municipal Services", index=True)
    status: Mapped[str] = mapped_column(String(20), default="Reported", index=True)
    image_path: Mapped[str | None] = mapped_column(String(240), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history: Mapped[list["ReportHistory"]] = relationship(back_populates="report", cascade="all, delete-orphan", order_by="ReportHistory.created_at")

class ReportHistory(Base):
    __tablename__ = "report_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    previous_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20))
    changed_by: Mapped[str] = mapped_column(String(100), default="Development admin")
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    report: Mapped[Report] = relationship(back_populates="history")
