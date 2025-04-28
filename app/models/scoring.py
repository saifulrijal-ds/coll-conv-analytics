from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from models.base import ScenarioType, ComplianceStatus, ScoreLevel

class OpeningScore(BaseModel):
    """Scoring for call opening section"""
    greeting_score: ScoreLevel = Field(
        default=ScoreLevel.NO_COMPLIANCE,
        description="Score for greeting, agent name and company name introduction"
    )
    greeting_evidence: Optional[str] = Field(
        default=None,
        description="Exact phrase from transcript showing greeting"
    )
    customer_name_verification: ComplianceStatus = Field(
        default=ComplianceStatus.NOT_APPLICABLE,
        description="Whether agent correctly verified customer name"
    )
    customer_verification_evidence: Optional[str] = Field(
        default=None,
        description="Evidence of customer verification"
    )
    mandatory_info_disclosed: List[str] = Field(
        default_factory=list,
        description="List of mandatory information disclosed (payment amount, penalty, past due)"
    )

class CommunicationScore(BaseModel):
    """Scoring for communication aspects"""
    voice_tone_score: ScoreLevel = Field(
        default=ScoreLevel.NO_COMPLIANCE,
        description="Score for voice tone, energy level and professionalism"
    )
    voice_tone_evidence: Optional[str] = Field(
        default=None,
        description="Evidence of voice tone quality"
    )
    speaking_pace_score: ScoreLevel = Field(
        default=ScoreLevel.NO_COMPLIANCE,
        description="Score for speaking pace and articulation"
    )
    speaking_pace_evidence: Optional[str] = Field(
        default=None,
        description="Evidence of speaking pace and clarity"
    )
    language_etiquette_score: ScoreLevel = Field(
        default=ScoreLevel.NO_COMPLIANCE,
        description="Score for language politeness and appropriateness"
    )
    language_evidence: List[str] = Field(
        default_factory=list,
        description="Examples of language usage"
    )

class NegotiationScore(BaseModel):
    """Scoring for negotiation skills"""
    negotiation_attempts: int = Field(
        default=0,
        description="Number of negotiation attempts made"
    )
    solutions_offered: List[str] = Field(
        default_factory=list,
        description="Solutions or alternatives offered during negotiation"
    )
    payment_commitment_obtained: bool = Field(
        default=False,
        description="Whether a payment commitment was obtained"
    )
    negotiation_evidence: List[str] = Field(
        default_factory=list,
        description="Key negotiation phrases from transcript"
    )

class KnockoutViolation(BaseModel):
    """Tracks knockout violations"""
    unauthorized_disclosure: bool = Field(
        default=False,
        description="Disclosed information to unauthorized party"
    )
    disclosure_evidence: Optional[str] = Field(
        default=None,
        description="Evidence of unauthorized disclosure"
    )
    ptp_cheating: bool = Field(
        default=False,
        description="Evidence of PTP cheating"
    )
    ptp_cheating_evidence: Optional[str] = Field(
        default=None,
        description="Evidence of PTP cheating"
    )
    other_violations: List[str] = Field(
        default_factory=list,
        description="Other compliance violations found"
    )

class QAScore(BaseModel):
    """Complete QA scoring for a call"""
    scenario_type: ScenarioType
    opening_score: OpeningScore = Field(default_factory=OpeningScore)
    communication_score: CommunicationScore = Field(default_factory=CommunicationScore)
    negotiation_score: Optional[NegotiationScore] = Field(default_factory=NegotiationScore)
    knockout_violations: KnockoutViolation = Field(default_factory=KnockoutViolation)
    total_score: float = Field(
        default=0.0,
        description="Calculated total score (0-1)"
    )
    score_breakdown: Dict[str, float] = Field(
        default_factory=lambda: {
            "opening": 0.0,
            "communication": 0.0,
            "negotiation": 0.0
        },
        description="Detailed score breakdown by category"
    )
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Areas identified for improvement"
    )
    evidence_highlights: List[str] = Field(
        default_factory=list,
        description="Key evidence supporting the scoring"
    )