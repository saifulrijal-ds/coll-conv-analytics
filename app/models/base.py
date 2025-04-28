from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum

class ScenarioType(str, Enum):
    PTP = "PTP"
    REFUSE_TO_PAY = "REFUSE_TO_PAY"
    TPC = "TPC"
    UNKNOWN = "UNKNOWN"

class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class ScoreLevel(str, Enum):
    NO_COMPLIANCE = "0"
    STANDARD_COMPLIANCE = "0.5"
    STRONG_COMPLIANCE = "1"

class Amount(BaseModel):
    """Represents a monetary amount"""
    value: float
    currenct: str = "IDR"
    type: str