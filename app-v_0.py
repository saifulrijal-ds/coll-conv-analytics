import streamlit as st
import os
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

# Schema definitions
class ScenarioType(str, Enum):
    PTP = "PTP"
    REFUSE_TO_PAY = "REFUSE_TO_PAY"
    TPC = "TPC"
    UNKNOWN = "UNKNOWN"

class Amount(BaseModel):
    value: float
    currency: str = "IDR"
    type: str

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
    """Additional details specific to PTP (Promise to Pay) scenario."""
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
    basic_info: BasicCallInfo
    ptp_details: Optional[PTPDetails] = None
    refuse_details: Optional[RefuseDetails] = None
    tpc_details: Optional[TPCDetails] = None
    call_summary: Optional[str] = None

# Enhanced prompt template
ANALYSIS_PROMPT = """
You are an expert collection call analyzer focusing on Indonesian language transcripts. Your primary task is to accurately classify and extract information from collection call transcripts.

## Scenario Classification Rules:

### 1. PTP (Promise to Pay)
Primary indicator:
- Customer explicitly provides a specific payment date
- Must be a direct promise from the customer (not a guess or suggestion from agent)
Examples:
- "Iya, saya bayar tanggal 8" (PTP)
- "Besok saya bayar" (PTP)
- "Insya Allah tanggal 27" (PTP)

Non-PTP examples:
- Agent: "Bisa bayar tanggal 8?" Customer: "Saya usahakan" (Not PTP - no firm commitment)
- "Mungkin minggu depan" (Not PTP - uncertain)

### 2. Third Party Contact (TPC)
Primary indicator:
- The person who answers is neither the customer nor their spouse
Look for:
- Questions about relationship to customer
- Reluctance to discuss payment details
- Requests to leave messages
Examples:
- "Saya adiknya"
- "Beliau sedang tidak ada"
- "Nanti saya sampaikan"

### 3. Refuse to Pay
Default classification if:
- No clear PTP date is given by customer
- Contact is with actual customer (not TPC)
Common indicators:
- Explicit refusal
- Providing reasons/obstacles
- Avoiding commitment
- Expressing inability to pay

## Key Information to Extract:

1. Basic Call Information:
- Agent and customer names
- Amounts mentioned (installment, penalties, total)
- Timestamps/duration
- Key dates mentioned

2. For PTP:
- Exact promised payment date
- Promised amount
- Number of negotiation attempts
- Any conditions attached to promise
- Strength of commitment

3. For Refuse to Pay:
- Main reason for refusal
- Customer's stated situation
- Solutions discussed
- Customer's responses to payment requests
- Type of refusal (explicit/implicit)

4. For TPC:
- Relationship to customer
- Whether message was delivered
- Any alternative contact information provided
- Level of cooperation from third party
- Verification attempts made

## Language Considerations:
- Pay attention to Indonesian politeness markers
- Note time-related expressions ("besok", "lusa", "minggu depan")
- Look for commitment-indicating words ("pasti", "akan", "janji")
- Watch for hesitation markers ("mungkin", "insya allah", "diusahakan")

Input Transcript to analyze:
{text}

Please analyze this transcript and extract the information according to these rules. Be explicit about why you classified it as a particular scenario type.
"""

# Initialize Streamlit app
st.set_page_config(
    page_title="Collection Call Analyzer",
    page_icon="📞",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .scenario-box {
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid rgba(0,0,0,0.1);
    }
    .ptp-box { 
        background-color: #e6ffe6; 
        border-left: 5px solid #28a745;
    }
    .refuse-box { 
        background-color: #ffe6e6; 
        border-left: 5px solid #dc3545;
    }
    .tpc-box { 
        background-color: #e6e6ff; 
        border-left: 5px solid #007bff;
    }
    .commitment-strong { color: #28a745; font-weight: bold; }
    .commitment-medium { color: #ffc107; font-weight: bold; }
    .commitment-weak { color: #dc3545; font-weight: bold; }
    .stMarkdown ul { padding-left: 20px; }
    .metric-card {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("📞 Collection Call Analysis Tool")
st.markdown("""
This tool analyzes collection call transcripts and provides detailed information about:
- Scenario classification (PTP/Refuse to Pay/TPC)
- Key information extraction
- Call summary and insights
""")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    # Model selection
    model_name = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4o"],
        index=0
    )
    
    # Classification rules
    with st.expander("Classification Rules"):
        st.markdown("""
        **PTP (Promise to Pay)**
        - Customer explicitly provides payment date
        - Direct promise from customer required
        - Clear commitment phrases
        
        **Third Party Contact (TPC)**
        - Person answering is not customer/spouse
        - Relationship verification required
        - Message delivery tracking
        
        **Refuse to Pay**
        - No clear PTP date given
        - Contact is with actual customer
        - Reason documentation needed
        """)

# File upload and text input
uploaded_file = st.file_uploader("Upload a transcript file", type=['txt'])
if uploaded_file is not None:
    transcript = uploaded_file.read().decode()
    st.text_area("Uploaded Transcript", transcript, height=200)
else:
    transcript = st.text_area(
        "Or paste your call transcript here",
        height=200,
        placeholder="Paste your call transcript here..."
    )

analyze_button = st.button("Analyze Transcript")

if analyze_button and transcript:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        try:
            with st.spinner("Analyzing transcript..."):
                # Get LLM pipeline and analyze
                llm = ChatOpenAI(model=model_name)
                structured_llm = llm.with_structured_output(schema=CallData)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", ANALYSIS_PROMPT),
                    ("human", "{text}")
                ])
                
                prompt_value = prompt.invoke({"text": transcript})
                result = structured_llm.invoke(prompt_value)
                
                # Display results in tabs
                tabs = st.tabs(["Analysis Results", "Detailed Information", "Raw Data"])

                
                # Analysis Results Tab
                with tabs[0]:
                    st.header("Analysis Results")
                    
                    # Top metrics row
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("""
                        <div class="metric-card">
                            <h3>Scenario Type</h3>
                            <p>{}</p>
                        </div>
                        """.format(result.basic_info.scenario_type), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="metric-card">
                            <h3>Call Duration</h3>
                            <p>{}</p>
                        </div>
                        """.format(result.basic_info.call_duration or "Not detected"), unsafe_allow_html=True)
                    
                    with col3:
                        total_amount = sum([amt.value for amt in result.basic_info.amounts_mentioned]) if result.basic_info.amounts_mentioned else 0
                        st.markdown("""
                        <div class="metric-card">
                            <h3>Total Amount</h3>
                            <p>IDR {:,.2f}</p>
                        </div>
                        """.format(total_amount), unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Classification reason
                    st.subheader("Classification Analysis")
                    st.markdown(f"**Reason**: {result.basic_info.classification_reason}")
                    
                    # Scenario-specific details
                    if result.ptp_details and result.basic_info.scenario_type == "PTP":
                        st.markdown('<div class="scenario-box ptp-box">', unsafe_allow_html=True)
                        st.subheader("PTP Details")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Promised Date**: {result.ptp_details.promised_date}")
                            if result.ptp_details.promised_amount:
                                st.markdown(f"**Promised Amount**: {result.ptp_details.promised_amount.value:,.2f} {result.ptp_details.promised_amount.currency}")
                            st.markdown(f"**Negotiation Attempts**: {result.ptp_details.negotiation_attempts or 'Not detected'}")
                        
                        with col2:
                            st.markdown(f"**Commitment Strength**: {result.ptp_details.commitment_strength}")
                            if result.ptp_details.commitment_phrases:
                                st.markdown("**Key Commitment Phrases**:")
                                for phrase in result.ptp_details.commitment_phrases:
                                    st.markdown(f"- {phrase}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    elif result.refuse_details and result.basic_info.scenario_type == "REFUSE_TO_PAY":
                        st.markdown('<div class="scenario-box refuse-box">', unsafe_allow_html=True)
                        st.subheader("Refuse to Pay Details")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Refusal Type**: {result.refuse_details.refusal_type}")
                            st.markdown(f"**Main Reason**: {result.refuse_details.reason}")
                            st.markdown(f"**Customer Situation**: {result.refuse_details.customer_situation}")
                        
                        with col2:
                            if result.refuse_details.solutions_discussed:
                                st.markdown("**Solutions Discussed**:")
                                for solution in result.refuse_details.solutions_discussed:
                                    st.markdown(f"- {solution}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    elif result.tpc_details and result.basic_info.scenario_type == "TPC":
                        st.markdown('<div class="scenario-box tpc-box">', unsafe_allow_html=True)
                        st.subheader("Third Party Contact Details")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Relationship**: {result.tpc_details.relationship_to_customer}")
                            st.markdown(f"**Message Delivered**: {'Yes' if result.tpc_details.message_delivered else 'No'}")
                            st.markdown(f"**Verification Attempted**: {'Yes' if result.tpc_details.verification_attempt else 'No'}")
                        
                        with col2:
                            if result.tpc_details.alternative_contacts:
                                st.markdown("**Alternative Contacts Provided**:")
                                for contact in result.tpc_details.alternative_contacts:
                                    st.markdown(f"- {contact}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed Information Tab
                with tabs[1]:
                    st.header("Detailed Information")
                    
                    # Basic Information
                    st.subheader("Basic Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Agent Name**: {result.basic_info.agent_name or 'Not detected'}")
                        st.markdown(f"**Customer Name**: {result.basic_info.customer_name or 'Not detected'}")
                    with col2:
                        st.markdown(f"**Call Duration**: {result.basic_info.call_duration or 'Not detected'}")
                        st.markdown(f"**Payment Date Mentioned**: {result.basic_info.payment_date_mentioned or 'None'}")
                    
                    # Amounts Section
                    if result.basic_info.amounts_mentioned:
                        st.subheader("Amounts Mentioned")
                        for amount in result.basic_info.amounts_mentioned:
                            st.markdown(f"- {amount.value:,.2f} {amount.currency} ({amount.type})")
                    
                    # Call Summary
                    st.subheader("Call Summary")
                    st.markdown(result.call_summary or "No summary available")
                
                # Raw Data Tab
                with tabs[2]:
                    st.header("Raw Data")
                    st.json(result.dict())
                    
                    # Download button
                    st.download_button(
                        "Download Analysis (JSON)",
                        data=json.dumps(result.dict(), indent=2, ensure_ascii=False),
                        file_name="call_analysis.json",
                        mime="application/json"
                    )

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.error("Please check your input and try again.")
