"""Sidebar components for the Streamlit application"""
import streamlit as st
from typing import Optional, Tuple
from utils.db_handler import db  # Add this import

def render_sidebar(default_model: str = "gpt-3.5-turbo") -> Tuple[str, str]:
    """
    Render the application sidebar
    
    Args:
        default_model (str): Default model name
        
    Returns:
        tuple: Selected model name and API key
    """
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key here"
        )
        
        # Model selection
        model_name = st.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4o"],
            index=["gpt-3.5-turbo", "gpt-4o"].index(default_model),
            help="Choose the model for analysis"
        )
        
        # Analysis history section
        st.markdown("---")
        if st.checkbox("Show Analysis History"):
            st.markdown("### Recent Analyses")
            recent = db.get_recent_analyses()
            for analysis in recent:
                if st.button(
                    f"Analysis {analysis['id']} - {analysis['scenario_type']} "
                    f"(Score: {analysis['qa_score']:.2f})",
                    key=f"history_{analysis['id']}"
                ):
                    # Load historical analysis
                    historical = db.get_analysis(analysis['id'])
                    if historical:
                        st.session_state.classification_results = historical['classification_data']
                        st.session_state.qa_score = historical['qa_data']
                        st.experimental_rerun()
        
        # About section
        st.markdown("---")
        st.markdown("""
        ### About
        This tool analyzes collection call transcripts and provides:
        - Call classification
        - QA scoring
        - Performance insights
        """)
        
        return model_name, api_key

def render_file_upload() -> Optional[str]:
    """
    Render the file upload section
    
    Returns:
        str: Uploaded transcript text or None
    """
    st.header("Upload Transcript")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a transcript file",
        type=['txt'],
        help="Upload a text file containing the call transcript"
    )
    
    # Manual input option
    use_manual_input = st.checkbox(
        "Or enter transcript manually",
        help="Type or paste the transcript text directly"
    )
    
    transcript_text = None
    
    if uploaded_file is not None:
        transcript_text = uploaded_file.read().decode()
    elif use_manual_input:
        transcript_text = st.text_area(
            "Enter transcript text",
            height=200,
            help="Paste or type the transcript text here"
        )
    
    if transcript_text:
        with st.expander("Preview Transcript"):
            st.text(transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text)
            
    return transcript_text
