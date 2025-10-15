from datetime import datetime, timezone

# Python Enum for statuses/kinds
from enum import Enum as PyEnum
# SQLAlchemy Enum TYPE for columns

from typing import List
from sqlalchemy import (
Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, Float, JSON, func
)
from sqlalchemy.orm import declarative_base, relationship
import uuid


Base = declarative_base()

class PadType(PyEnum):
    TRANSIT = "TRANSIT"
    FREIGHT = "FREIGHT"

class PadStatus(PyEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"

class BrakePad(Base):
    __tablename__ = "brake_pads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    serial_number = Column(String, unique=True, nullable=False)
    pad_type = Column(SAEnum(PadType, name="pad_type"), nullable=False)
    status   = Column(SAEnum(PadStatus, name="pad_status"), nullable=False)
    batch_code = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey("assembly_lines.id"), nullable=False)
    belt_id = Column(Integer, ForeignKey("belts.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    material_mix = relationship("MaterialMix", back_populates="brakepad", uselist=False,
                                cascade="all, delete-orphan")
    # NEW: relationship so we can joinedload it
    stage = relationship("Stage", back_populates="pads")
    predictions = relationship("Prediction", back_populates="brakepad", cascade="all, delete-orphan")

class AssemblyLine(Base):
    __tablename__ = "assembly_lines"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    belts = relationship("ConveyorBelt", back_populates="line", cascade="all, delete-orphan")
    stages = relationship("Stage", back_populates="line", cascade="all, delete-orphan")

class ConveyorBelt(Base):
    __tablename__ = "belts"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey("assembly_lines.id"), nullable=False)
    line = relationship("AssemblyLine", back_populates="belts")

class Stage(Base):
    __tablename__ = "stages"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    line_id = Column(Integer, ForeignKey("assembly_lines.id"), nullable=False)
    line = relationship("AssemblyLine", back_populates="stages")
    # NEW: backref to pads
    pads = relationship("BrakePad", back_populates="stage")

class MaterialMix(Base):
    __tablename__ = "material_mixes"
    id = Column(Integer, primary_key=True)
    brakepad_id = Column(String, ForeignKey("brake_pads.id"), nullable=False, unique=True)
    resin_pct = Column(Float)
    fiber_pct = Column(Float)
    metal_powder_pct = Column(Float)
    filler_pct = Column(Float)
    abrasives_pct = Column(Float)
    binder_pct = Column(Float)
    temp_c = Column(Float)
    pressure_mpa = Column(Float)
    cure_time_s = Column(Float)
    moisture_pct = Column(Float)
    brakepad = relationship("BrakePad", back_populates="material_mix")

class PredictionKind(PyEnum):
    MIX = "MIX"
    IMAGE = "IMAGE"

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    brakepad_id = Column(String, ForeignKey("brake_pads.id"), nullable=True)  # ← allow NULL
    kind = Column(SAEnum(PredictionKind, name="prediction_kind"), nullable=False)
    model_version = Column(String, nullable=False)
    label = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    explanation_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    brakepad = relationship("BrakePad", back_populates="predictions")