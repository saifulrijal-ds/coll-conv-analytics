"""Dashboard components for the Streamlit application"""
import streamlit as st
from typing import Dict, List, Any
import pandas as pd
from models.classification import CallData
from models.scoring import QAScore

def render_dashboard(call_data: CallData, qa_score: QAScore):
    """
    Render the analysis dashboard
    
    Args:
        call_data (CallData): Call classification data
        qa_score (QAScore): QA scoring data
    """
    st.header("Analysis Dashboard")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card(
            "Scenario Type",
            call_data.basic_info.scenario_type,
            get_scenario_icon(call_data.basic_info.scenario_type)
        )
        
    with col2:
        render_metric_card(
            "QA Score",
            f"{qa_score.total_score * 100:.1f}%",
            "✨"
        )
        
    with col3:
        status = "PASS" if qa_score.total_score >= 0.85 else "FAIL"
        render_metric_card(
            "Status",
            status,
            "✅" if status == "PASS" else "❌"
        )
    
    # Score breakdown
    st.subheader("Score Breakdown")
    render_score_breakdown(qa_score.score_breakdown)
    
    # Key findings
    st.subheader("Key Findings")
    render_findings(call_data, qa_score)
    
def render_metric_card(title: str, value: str, icon: str):
    """Render a metric card with consistent styling"""
    st.markdown(
        f"""
        <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;'>
            <h3>{icon} {title}</h3>
            <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_scenario_icon(scenario_type: str) -> str:
    """Get appropriate icon for scenario type"""
    icons = {
        "PTP": "🤝",
        "REFUSE_TO_PAY": "⛔",
        "TPC": "👥",
        "UNKNOWN": "❓"
    }
    return icons.get(scenario_type, "❓")

def render_score_breakdown(score_breakdown: Dict[str, float]):
    """Render score breakdown chart"""
    # Convert score breakdown to DataFrame
    df = pd.DataFrame([
        {"Category": k, "Score": v * 100} 
        for k, v in score_breakdown.items()
    ])
    
    # Create bar chart
    st.bar_chart(
        df.set_index("Category"),
        height=200
    )

def render_findings(call_data: CallData, qa_score: QAScore):
    """Render key findings from the analysis"""
    # Strengths
    st.markdown("##### 💪 Strengths")
    strengths = extract_strengths(qa_score)
    for strength in strengths:
        st.markdown(f"- {strength}")
    
    # Areas for Improvement
    if qa_score.improvement_areas:
        st.markdown("##### 🎯 Areas for Improvement")
        for area in qa_score.improvement_areas:
            st.markdown(f"- {area}")
    
    # Critical Issues
    if has_critical_issues(qa_score):
        st.markdown("##### ⚠️ Critical Issues")
        for issue in extract_critical_issues(qa_score):
            st.error(issue)

def extract_strengths(qa_score: QAScore) -> List[str]:
    """Extract strengths from QA score"""
    strengths = []
    
    # Check opening scores
    if float(qa_score.opening_score.greeting_score.value) >= 0.8:
        strengths.append("Strong opening and greeting")
        
    # Check communication scores
    if float(qa_score.communication_score.voice_tone_score.value) >= 0.8:
        strengths.append("Excellent voice tone and energy")
    
    if float(qa_score.communication_score.language_etiquette_score.value) >= 0.8:
        strengths.append("Professional language and etiquette")
    
    # Check negotiation if applicable
    if qa_score.negotiation_score and qa_score.negotiation_score.payment_commitment_obtained:
        strengths.append("Successful payment commitment obtained")
    
    return strengths

def has_critical_issues(qa_score: QAScore) -> bool:
    """Check for critical issues in QA score"""
    return (
        qa_score.knockout_violations.unauthorized_disclosure or
        qa_score.knockout_violations.ptp_cheating or
        qa_score.knockout_violations.other_violations or
        qa_score.total_score < 0.7
    )

def extract_critical_issues(qa_score: QAScore) -> List[str]:
    """Extract critical issues from QA score"""
    issues = []
    
    if qa_score.knockout_violations.unauthorized_disclosure:
        issues.append("Unauthorized information disclosure detected")
        
    if qa_score.knockout_violations.ptp_cheating:
        issues.append("PTP cheating detected")
        
    issues.extend(qa_score.knockout_violations.other_violations)
    
    if qa_score.total_score < 0.7:
        issues.append(f"Overall score ({qa_score.total_score * 100:.1f}%) below minimum threshold")
    
    return issues
