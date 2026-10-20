from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import Base, engine
from .config import FRONTEND_ORIGINS, UPLOAD_DIR
from . import models
from .routers import reports, dashboard

Base.metadata.create_all(bind=engine)
app = FastAPI(title="NEXUS CITY AI API", description="Civic infrastructure reporting and monitoring prototype. AI analysis currently uses a rule-based fallback.", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True, allow_methods=["GET","POST","PATCH","OPTIONS"], allow_headers=["*"])
app.include_router(reports.router); app.include_router(dashboard.router)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
@app.get("/", include_in_schema=False)
def local_preview(): return FileResponse(str(__import__("pathlib").Path(__file__).parent / "static" / "index.html"))
@app.get("/api/health", tags=["health"])
def health(): return {"status":"ok","application":"NEXUS CITY AI","ai_mode":"rule-based fallback","database":"configured"}
