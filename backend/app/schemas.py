from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

CATEGORIES = ["Flooding", "Water Leakage", "Waterlogging", "Blocked Drainage", "Potholes", "Road Damage", "Streetlight Failure", "Landslide Risk", "Other Infrastructure Issues"]
STATUSES = ["Reported", "Under Review", "In Progress", "Resolved"]
SEVERITIES = ["Low", "Medium", "High"]

class ReportCreate(BaseModel):
    title: str = Field(min_length=5, max_length=140)
    description: str = Field(min_length=10, max_length=5000)
    citizen_category: str
    location_name: str = Field(min_length=2, max_length=220)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("citizen_category")
    @classmethod
    def category_valid(cls, v):
        if v not in CATEGORIES: raise ValueError("Choose a valid infrastructure category")
        return v

class ReportUpdate(BaseModel):
    status: str | None = None
    department: str | None = Field(default=None, max_length=80)
    severity: str | None = None
    change_note: str | None = Field(default=None, max_length=1000)

    @field_validator("status")
    @classmethod
    def status_valid(cls, v):
        if v is not None and v not in STATUSES: raise ValueError("Invalid status")
        return v
    @field_validator("severity")
    @classmethod
    def severity_valid(cls, v):
        if v is not None and v not in SEVERITIES: raise ValueError("Invalid severity")
        return v

class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    public_report_id: str
    title: str
    description: str
    citizen_category: str
    ai_suggested_category: str
    location_name: str
    latitude: float | None
    longitude: float | None
    severity: str
    ai_explanation: str
    ai_summary: str
    department: str
    status: str
    image_path: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    previous_status: str | None
    new_status: str
    changed_by: str
    change_note: str | None
    created_at: datetime
