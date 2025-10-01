from datetime import datetime
from enum import Enum
from typing import List
from sqlalchemy import (
Column, Integer, String, DateTime, Enum as SqlEnum, ForeignKey, Float, JSON
)
from sqlalchemy.orm import declarative_base, relationship
import uuid


Base = declarative_base()