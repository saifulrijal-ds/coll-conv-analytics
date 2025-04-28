"""QA Scoring display components for the Streamlit application"""
import streamlit as st
from typing import Dict, Any
from models.scoring import QAScore, ScoreLevel

def render_qa_score(score: QAScore, min_score: float = 0.85):
    """
    Display QA scoring results
    
    Args:
        score (QAScore): QA scoring results
        min_score (float): Minimum passing score threshold (default: 0.85)
    """
    st.header("QA Scoring Analysis")
    
    # Overall score display
    total_score_percentage = score.total_score * 100
    score_color = get_score_color(total_score_percentage)
    passing_status = "Pass" if score.total_score >= min_score else "Needs Improvement"
    
    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px; background-color: {score_color}; border-radius: 10px;'>
            <h2 style='color: white;'>Overall Score: {total_score_percentage:.1f}%</h2>
            <p style='color: white;'>{passing_status}</p>
            <p style='color: white; font-size: 0.8em;'>Minimum Required: {min_score * 100:.1f}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Knockout violations check
    if has_knockout_violations(score.knockout_violations):
        st.error("⚠️ Critical Issues Detected!")
        display_knockout_violations(score.knockout_violations)
    
    # Detailed scoring sections
    st.markdown("### Detailed Scoring")
    tabs = st.tabs(["Opening", "Communication", "Negotiation"])
    
    with tabs[0]:
        display_opening_scores(score.opening_score)
    
    with tabs[1]:
        display_communication_scores(score.communication_score)
    
    with tabs[2]:
        if score.negotiation_score:
            display_negotiation_scores(score.negotiation_score)
        else:
            st.info("No negotiation scoring applicable for this call type")
    
    # Score comparison
    st.markdown("### Score Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Score vs Threshold",
            f"{total_score_percentage:.1f}%",
            f"{(score.total_score - min_score) * 100:+.1f}%",
            delta_color="normal" if score.total_score >= min_score else "inverse"
        )
    
    # Improvement areas
    if score.improvement_areas:
        st.markdown("### Areas for Improvement")
        for area in score.improvement_areas:
            st.warning(area)
    
    # Evidence highlights
    if score.evidence_highlights:
        with st.expander("Evidence Highlights"):
            for evidence in score.evidence_highlights:
                st.markdown(f"- _{evidence}_")

def get_score_color(score_percentage: float) -> str:
    """Get color based on score percentage"""
    if score_percentage >= 90:
        return "#28a745"  # Green
    elif score_percentage >= 85:
        return "#17a2b8"  # Blue
    elif score_percentage >= 70:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def has_knockout_violations(violations) -> bool:
    """Check if there are any knockout violations"""
    return (violations.unauthorized_disclosure or 
            violations.ptp_cheating or 
            violations.other_violations)

def display_knockout_violations(violations):
    """Display knockout violations details"""
    if violations.unauthorized_disclosure:
        st.error(f"Unauthorized Information Disclosure\n{violations.disclosure_evidence}")
    
    if violations.ptp_cheating:
        st.error(f"PTP Cheating Detected\n{violations.ptp_cheating_evidence}")
    
    for violation in violations.other_violations:
        st.error(f"Policy Violation: {violation}")

def display_opening_scores(opening_score):
    """Display opening section scores"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Greeting")
        display_score_value("Greeting Score", opening_score.greeting_score)
        if opening_score.greeting_evidence:
            st.markdown(f"Evidence: _{opening_score.greeting_evidence}_")
    
    with col2:
        st.markdown("#### Customer Verification")
        st.write(f"Status: {opening_score.customer_name_verification}")
        if opening_score.customer_verification_evidence:
            st.markdown(f"Evidence: _{opening_score.customer_verification_evidence}_")
    
    st.markdown("#### Mandatory Information")
    for info in opening_score.mandatory_info_disclosed:
        st.markdown(f"- {info}")

def display_communication_scores(communication_score):
    """Display communication scores"""
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("#### Voice Tone")
        display_score_value("Voice Quality", communication_score.voice_tone_score)
        if communication_score.voice_tone_evidence:
            st.markdown(f"Evidence: _{communication_score.voice_tone_evidence}_")
    
    with cols[1]:
        st.markdown("#### Speaking Pace")
        display_score_value("Pace Score", communication_score.speaking_pace_score)
        if communication_score.speaking_pace_evidence:
            st.markdown(f"Evidence: _{communication_score.speaking_pace_evidence}_")
    
    with cols[2]:
        st.markdown("#### Language Etiquette")
        display_score_value("Language Score", communication_score.language_etiquette_score)
        if communication_score.language_evidence:
            for evidence in communication_score.language_evidence:
                st.markdown(f"- _{evidence}_")

def display_negotiation_scores(negotiation_score):
    """Display negotiation scores"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Negotiation Attempts", negotiation_score.negotiation_attempts)
        st.write("Payment Commitment:", 
                "✅ Obtained" if negotiation_score.payment_commitment_obtained 
                else "❌ Not Obtained")
    
    with col2:
        st.markdown("#### Solutions Offered")
        for solution in negotiation_score.solutions_offered:
            st.markdown(f"- {solution}")
    
    if negotiation_score.negotiation_evidence:
        st.markdown("#### Key Negotiation Phrases")
        for evidence in negotiation_score.negotiation_evidence:
            st.markdown(f"- _{evidence}_")

def display_score_value(label: str, score: ScoreLevel):
    """Display a score value with appropriate styling"""
    score_value = float(score.value)
    score_color = get_score_color(score_value * 100)
    
    st.markdown(
        f"""
        <div style='padding: 10px; border-radius: 5px; background-color: {score_color}; color: white;'>
            <b>{label}:</b> {score_value:.1f}
        </div>
        """,
        unsafe_allow_html=True
    )
