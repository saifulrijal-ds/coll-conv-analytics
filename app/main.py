"""Main Streamlit application for call analysis"""
import os
import streamlit as st
import json
from typing import Optional, Tuple

# Import UI components
from ui.sidebar import render_sidebar, render_file_upload
from ui.analysis import render_classification_results, render_error_message
from ui.scoring import render_qa_score
from ui.dashboard import render_dashboard

# Import analyzers
from analyzers.classification import CallClassificationAnalyzer
from analyzers.scoring import QAScoringAnalyzer

# Import utils
from utils.common import clean_transcript
from utils.file_handler import FileHandler
from utils.config import config
from utils.db_handler import db

# Page config
st.set_page_config(
    page_title="Call Analysis Dashboard",
    page_icon="📞",
    layout="wide"
)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    if 'classification_results' not in st.session_state:
        st.session_state.classification_results = None
    if 'qa_score' not in st.session_state:
        st.session_state.qa_score = None
    if 'file_handler' not in st.session_state:
        st.session_state.file_handler = FileHandler(config.get_config()["data_dir"])

def main():
    """Main application function"""
    # Initialize session
    init_session_state()
    
    # Get configuration
    app_config = config.get_config()
    qa_weights = config.get_qa_weights()
    
    # Render sidebar and get config updates
    model_name, api_key = render_sidebar(
        default_model=app_config.get("model_name")
    )
    
    # Update API key if provided through UI
    if api_key:
        app_config["api_key"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    elif not app_config.get("api_key"):
        st.warning("Please enter your OpenAI API key in the sidebar or set it in .env file.")
        return
        
    # Get transcript input
    transcript = render_file_upload()
    
    if transcript:
        # Clean transcript
        cleaned_transcript = clean_transcript(transcript)
        
        # Analysis section
        st.markdown("---")
        analyze_button = st.button("Start Analysis", type="primary")
        
        if analyze_button:
            try:
                with st.spinner("Analyzing call..."):
                    # Perform call classification
                    classifier = CallClassificationAnalyzer(
                        model_name=model_name,
                        temperature=app_config.get("temperature", 0)
                    )
                    classification_results = classifier.analyze_transcript(cleaned_transcript)
                    st.session_state.classification_results = classification_results
                    
                    # Perform QA scoring
                    scorer = QAScoringAnalyzer(
                        model_name=model_name,
                        temperature=app_config.get("temperature", 0)
                    )
                    qa_score = scorer.analyze_transcript(
                        transcript=cleaned_transcript,
                        scenario_type=classification_results.basic_info.scenario_type
                    )
                    st.session_state.qa_score = qa_score
                    
                    # Save analysis results
                    st.session_state.file_handler.save_analysis(
                        {
                            "classification": classification_results.model_dump(),
                            "qa_score": qa_score.model_dump()
                        },
                        "latest_analysis"
                    )

                    analysis_id = db.save_analysis(
                        transcript=cleaned_transcript,
                        classification_data=classification_results.model_dump(),
                        qa_data=qa_score.model_dump(),
                        metadata={
                            "model_name": model_name,
                            "temperature": app_config.get("temperature", 0)
                        }
                    )
                    st.session_state.current_analysis_id = analysis_id
                    
            except Exception as e:
                render_error_message(str(e))
                return
        
        # Display results if available
        if st.session_state.classification_results and st.session_state.qa_score:
            # Dashboard tab
            tabs = st.tabs(["Dashboard", "Classification", "QA Score"])
            
            with tabs[0]:
                render_dashboard(
                    st.session_state.classification_results,
                    st.session_state.qa_score
                )
                
            with tabs[1]:
                render_classification_results(st.session_state.classification_results)
                
            with tabs[2]:
                render_qa_score(
                    st.session_state.qa_score,
                    min_score=app_config.get("min_qa_score", 0.85)
                )
                
            # Download options
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                # Get the analysis data and convert to JSON string
                analysis_data = st.session_state.file_handler.load_analysis("latest_analysis")
                if analysis_data:
                    json_str = json.dumps(analysis_data, indent=2)
                    if st.download_button(
                        "Download Analysis Results (JSON)",
                        data=json_str,
                        file_name="analysis_results.json",
                        mime="application/json"
                    ):
                        st.success("Analysis results downloaded!")
            
            with col2:
                if transcript:
                    if st.download_button(
                        "Download Transcript",
                        data=transcript,
                        file_name="transcript.txt",
                        mime="text/plain"
                    ):
                        st.success("Transcript downloaded!")

if __name__ == "__main__":
    main()
