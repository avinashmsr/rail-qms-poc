from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_db
from ..models import (
    AssemblyLine,
    ConveyorBelt,
    Stage,
    BrakePad,
    PadStatus,
)

router = APIRouter()