"""Analysis display components for the Streamlit application"""
import streamlit as st
from typing import Optional, Dict, Any
from models.classification import CallData
from utils.common import format_currency

def render_classification_results(results: CallData):
    """
    Display call classification results
    
    Args:
        results (CallData): Classification analysis results
    """
    st.header("Call Classification Results")
    
    # Display scenario type with appropriate styling
    scenario_colors = {
        "PTP": "🟢 Promise to Pay",
        "REFUSE_TO_PAY": "🔴 Refuse to Pay",
        "TPC": "🔵 Third Party Contact",
        "UNKNOWN": "⚪ Unknown"
    }
    
    st.subheader(scenario_colors.get(results.basic_info.scenario_type, "Unknown Scenario"))
    
    # Basic information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Call Details")
        st.write(f"🎯 Agent: {results.basic_info.agent_name or 'Not detected'}")
        st.write(f"👤 Customer: {results.basic_info.customer_name or 'Not detected'}")
        if results.basic_info.call_duration:
            st.write(f"⏱️ Duration: {results.basic_info.call_duration}")
            
    with col2:
        st.markdown("#### Amount Information")
        if results.basic_info.amounts_mentioned:
            for amount in results.basic_info.amounts_mentioned:
                st.write(f"💰 {format_currency(amount.value)}: {amount.type}")
                
    # Classification reasoning
    st.markdown("#### Classification Reasoning")
    st.info(results.basic_info.classification_reason)
    
    # Scenario-specific details
    if results.ptp_details:
        display_ptp_details(results.ptp_details)
    elif results.refuse_details:
        display_refuse_details(results.refuse_details)
    elif results.tpc_details:
        display_tpc_details(results.tpc_details)

def display_ptp_details(ptp_details):
    """Display PTP-specific details"""
    st.markdown("#### Promise to Pay Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📅 Promised Date: {ptp_details.promised_date or 'Not specified'}")
        if ptp_details.promised_amount:
            st.write(f"💵 Promised Amount: {format_currency(ptp_details.promised_amount.value)}")
            
    with col2:
        st.write(f"🎯 Negotiation Attempts: {ptp_details.negotiation_attempts or 0}")
        st.write(f"💪 Commitment Strength: {ptp_details.commitment_strength}")
        
    if ptp_details.commitment_phrases:
        st.markdown("#### Key Commitment Phrases")
        for phrase in ptp_details.commitment_phrases:
            st.markdown(f"- _{phrase}_")

def display_refuse_details(refuse_details):
    """Display Refuse to Pay specific details"""
    st.markdown("#### Refusal Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"❌ Refusal Type: {refuse_details.refusal_type}")
        st.write(f"🔍 Main Reason: {refuse_details.reason or 'Not specified'}")
        
    with col2:
        st.write("Customer Situation:")
        st.write(refuse_details.customer_situation or "Not specified")
        
    if refuse_details.solutions_discussed:
        st.markdown("#### Solutions Discussed")
        for solution in refuse_details.solutions_discussed:
            st.markdown(f"- {solution}")

def display_tpc_details(tpc_details):
    """Display Third Party Contact specific details"""
    st.markdown("#### Third Party Contact Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"👥 Relationship: {tpc_details.relationship_to_customer or 'Unknown'}")
        st.write(f"✉️ Message Delivered: {'Yes' if tpc_details.message_delivered else 'No'}")
        
    with col2:
        st.write(f"✅ Verification Attempted: {'Yes' if tpc_details.verification_attempt else 'No'}")
        
    if tpc_details.alternative_contacts:
        st.markdown("#### Alternative Contacts")
        for contact in tpc_details.alternative_contacts:
            st.markdown(f"- {contact}")

def render_error_message(error: str):
    """Display error message"""
    st.error(f"Analysis Error: {error}")
    st.markdown("""
    Please check:
    - Transcript content is valid
    - API key is correct
    - Selected model is available
    """)
