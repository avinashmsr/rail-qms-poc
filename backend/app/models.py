from datetime import datetime, timezone
from enum import Enum
from typing import List
from sqlalchemy import (
Column, Integer, String, DateTime, Enum as SqlEnum, ForeignKey, Float, JSON
)
from sqlalchemy.orm import declarative_base, relationship
import uuid


Base = declarative_base()

class PadType(str, Enum):
    TRANSIT = "TRANSIT"
    FREIGHT = "FREIGHT"

class PadStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"

class BrakePad(Base):
    __tablename__ = "brake_pads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    serial_number = Column(String, unique=True, nullable=False)
    pad_type = Column(SqlEnum(PadType), nullable=False)
    batch_code = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey("assembly_lines.id"), nullable=False)
    belt_id = Column(Integer, ForeignKey("belts.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    status = Column(SqlEnum(PadStatus), default=PadStatus.IN_PROGRESS)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    material_mix = relationship("MaterialMix", back_populates="brakepad", uselist=False,
                                cascade="all, delete-orphan")
    # NEW: relationship so we can joinedload it
    stage = relationship("Stage", back_populates="pads")

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