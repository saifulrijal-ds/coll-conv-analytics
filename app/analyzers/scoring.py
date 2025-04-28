from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from models.base  import ScenarioType
from models.scoring import QAScore
from analyzers.prompts import QA_SCORING_PROMPT, get_scenario_specific_additions

class QAScoringAnalyzer:
    """Analyzes call transcripts for QA scoring"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0):
        """Initialize the analyzer with specified model"""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        self.structured_llm = self.llm.with_structured_output(QAScore)
        
    def analyze_transcript(self, 
                         transcript: str,
                         scenario_type: ScenarioType) -> QAScore:
        """
        Analyze a call transcript and generate QA scores
        
        Args:
            transcript (str): The call transcript text
            scenario_type (ScenarioType): Previously identified scenario type
            
        Returns:
            QAScore: Structured QA scoring data
            
        Raises:
            Exception: If analysis fails
        """
        try:
            # Create base prompt
            base_prompt = QA_SCORING_PROMPT
            
            # Add scenario-specific criteria
            scenario_additions = get_scenario_specific_additions(scenario_type.value)
            final_prompt = base_prompt + scenario_additions
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(final_prompt)
            
            # Generate prompt values
            prompt_value = prompt.invoke({
                "text": transcript,
                "scenario_type": scenario_type.value
            })
            
            # Get structured output
            result = self.structured_llm.invoke(prompt_value)
            
            # Validate score_breakdown
            if not result.score_breakdown:
                result.score_breakdown = {
                    "opening": 0.0,
                    "communication": 0.0,
                    "negotiation": 0.0
                }
            
            return result
            
        except Exception as e:
            print(f"Raw scoring error: {str(e)}")  # For debugging
            raise Exception(f"Error during QA scoring: {str(e)}")
            
    def calculate_section_scores(self, score: QAScore) -> dict:
        """
        Calculate detailed section scores
        
        Args:
            score (QAScore): The QA scoring result
            
        Returns:
            dict: Detailed breakdown of section scores
        """
        section_scores = {
            "opening": {
                "raw_score": 0.0,
                "weighted_score": 0.0,
                "components": {}
            },
            "communication": {
                "raw_score": 0.0,
                "weighted_score": 0.0,
                "components": {}
            },
            "negotiation": {
                "raw_score": 0.0,
                "weighted_score": 0.0,
                "components": {}
            }
        }
        
        # Calculate opening scores
        if score.opening_score:
            section_scores["opening"]["components"]["greeting"] = float(score.opening_score.greeting_score.value)
            section_scores["opening"]["components"]["customer_verification"] = (
                1.0 if score.opening_score.customer_name_verification == "COMPLIANT" else 0.0
            )
            section_scores["opening"]["raw_score"] = sum(section_scores["opening"]["components"].values()) / 2
            section_scores["opening"]["weighted_score"] = section_scores["opening"]["raw_score"] * 0.06
            
        # Calculate communication scores
        if score.communication_score:
            section_scores["communication"]["components"]["voice_tone"] = float(score.communication_score.voice_tone_score.value)
            section_scores["communication"]["components"]["speaking_pace"] = float(score.communication_score.speaking_pace_score.value)
            section_scores["communication"]["components"]["language"] = float(score.communication_score.language_etiquette_score.value)
            section_scores["communication"]["raw_score"] = sum(section_scores["communication"]["components"].values()) / 3
            section_scores["communication"]["weighted_score"] = section_scores["communication"]["raw_score"] * 0.25
            
        # Calculate negotiation scores if applicable
        if score.negotiation_score and score.scenario_type in [ScenarioType.PTP, ScenarioType.REFUSE_TO_PAY]:
            effectiveness = 1.0 if score.negotiation_score.payment_commitment_obtained else 0.0
            solutions = min(len(score.negotiation_score.solutions_offered) * 0.2, 1.0)
            attempts = min(score.negotiation_score.negotiation_attempts * 0.2, 1.0)
            
            section_scores["negotiation"]["components"]["effectiveness"] = effectiveness
            section_scores["negotiation"]["components"]["solutions"] = solutions
            section_scores["negotiation"]["components"]["attempts"] = attempts
            section_scores["negotiation"]["raw_score"] = (effectiveness + solutions + attempts) / 3
            section_scores["negotiation"]["weighted_score"] = section_scores["negotiation"]["raw_score"] * 0.40
            
        return section_scores
