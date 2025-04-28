from typing import Optional, List
from pydantic import BaseModel, Field
from models.base import ScenarioType, Amount

class BasicCallInfo(BaseModel):
    """Basic information extracted from a collection call."""
    agent_name: Optional[str] = Field(
        default=None, 
        description="Name of the collection agent"
    )
    customer_name: Optional[str] = Field(
        default=None, 
        description="Name of the customer being contacted"
    )
    scenario_type: ScenarioType = Field(
        default=ScenarioType.UNKNOWN,
        description="Type of collection scenario identified"
    )
    classification_reason: str = Field(
        default="",
        description="Explanation of why this scenario type was chosen"
    )
    call_duration: Optional[str] = Field(
        default=None,
        description="Duration of the call in timestamp format"
    )
    amounts_mentioned: List[Amount] = Field(
        default_factory=list,
        description="List of monetary amounts mentioned in the call"
    )
    payment_date_mentioned: Optional[str] = Field(
        default=None,
        description="Any payment date mentioned in the conversation"
    )

class PTPDetails(BaseModel):
    """Additional details specific to PTP scenario."""
    promised_date: Optional[str] = Field(
        default=None,
        description="Date customer promised to pay"
    )
    promised_amount: Optional[Amount] = Field(
        default=None,
        description="Amount customer promised to pay"
    )
    negotiation_attempts: Optional[int] = Field(
        default=None,
        description="Number of times agent attempted to negotiate payment"
    )
    commitment_strength: str = Field(
        default="medium",
        description="Assessment of how strong the commitment seems (strong/medium/weak)"
    )
    commitment_phrases: List[str] = Field(
        default_factory=list,
        description="Key phrases that indicated commitment"
    )

class RefuseDetails(BaseModel):
    """Additional details specific to Refuse to Pay scenario."""
    reason: Optional[str] = Field(
        default=None,
        description="Main reason given for refusing payment"
    )
    customer_situation: Optional[str] = Field(
        default=None,
        description="Description of customer's stated situation or obstacles"
    )
    refusal_type: str = Field(
        default="implicit",
        description="Whether refusal was explicit or implicit"
    )
    solutions_discussed: List[str] = Field(
        default_factory=list,
        description="Solutions or alternatives discussed during call"
    )

class TPCDetails(BaseModel):
    """Additional details specific to Third Party Contact scenario."""
    relationship_to_customer: Optional[str] = Field(
        default=None,
        description="Relationship of the contacted person to the customer"
    )
    message_delivered: Optional[bool] = Field(
        default=None,
        description="Whether a message was successfully delivered"
    )
    verification_attempt: bool = Field(
        default=False,
        description="Whether agent attempted to verify relationship"
    )
    alternative_contacts: List[str] = Field(
        default_factory=list,
        description="Any alternative contact information provided"
    )

class CallData(BaseModel):
    """Complete call analysis data"""
    basic_info: BasicCallInfo
    ptp_details: Optional[PTPDetails] = None
    refuse_details: Optional[RefuseDetails] = None
    tpc_details: Optional[TPCDetails] = None
    call_summary: Optional[str] = None
