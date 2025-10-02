from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import lines, pads, stats

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Rail QMS PoC", version="0.1.0")


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(lines.router, prefix="/lines", tags=["lines"])
app.include_router(pads.router, prefix="/pads", tags=["pads"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])


@app.get("/")
def root():
return {"ok": True, "service": "Rail QMS PoC"}