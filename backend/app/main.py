from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import lines, pads, stats, setup

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Rail QMS PoC", version="0.1.0")

origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.include_router(lines.router, prefix="/lines", tags=["lines"])
app.include_router(pads.router, prefix="/pads", tags=["pads"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(setup.router, prefix="/setup", tags=["setup"])


@app.get("/")
def root():
    return {"ok": True, "service": "Rail QMS PoC"}