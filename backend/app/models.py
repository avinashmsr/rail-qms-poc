from datetime import datetime
from enum import Enum
from typing import List
from sqlalchemy import (
Column, Integer, String, DateTime, Enum as SqlEnum, ForeignKey, Float, JSON
)
from sqlalchemy.orm import declarative_base, relationship
import uuid


Base = declarative_base()

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
created_at = Column(DateTime, default=datetime.utcnow)

class AssemblyLine(Base):
__tablename__ = "assembly_lines"
id = Column(Integer, primary_key=True)
name = Column(String, unique=True, nullable=False)
belts = relationship("ConveyorBelt", back_populates="line", cascade="all, delete-orphan")
stages = relationship("Stage", back_populates="line", cascade="all, delete-orphan")

class PadStatus(str, Enum):
IN_PROGRESS = "IN_PROGRESS"
PASSED = "PASSED"
FAILED = "FAILED"