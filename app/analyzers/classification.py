from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from models.classification import CallData
from analyzers.prompts import CLASSIFICATION_PROMPT

class CallClassificationAnalyzer:
    """Analyzes call transcripts to classify scenario type and extract basic information"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0):
        """Initialize the analyzer with specified model"""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        self.structured_llm = self.llm.with_structured_output(CallData)
        
    def analyze_transcript(self, transcript: str) -> CallData:
        """
        Analyze a call transcript to classify scenario and extract information
        
        Args:
            transcript (str): The call transcript text
            
        Returns:
            CallData: Structured data about the call including classification
            
        Raises:
            Exception: If analysis fails
        """
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT)
            
            # Generate prompt values
            prompt_value = prompt.invoke({"text": transcript})
            
            # Get structured output
            result = self.structured_llm.invoke(prompt_value)
            
            return result
            
        except Exception as e:
            print(f"Raw classification error: {str(e)}")  # For debugging
            raise Exception(f"Error during call classification: {str(e)}")
    
    def get_confidence_metrics(self, result: CallData) -> dict:
        """
        Calculate confidence metrics for the classification
        
        Args:
            result (CallData): The classification result
            
        Returns:
            dict: Confidence metrics for different aspects of the classification
        """
        metrics = {
            "classification_confidence": 0.0,
            "information_completeness": 0.0,
            "evidence_strength": 0.0
        }
        
        # Calculate classification confidence
        if result.basic_info.classification_reason:
            metrics["classification_confidence"] = 0.8
            
        # Calculate information completeness
        complete_fields = 0
        total_fields = 0
        
        for field, value in result.basic_info.dict().items():
            total_fields += 1
            if value is not None and value != "" and value != []:
                complete_fields += 1
                
        metrics["information_completeness"] = complete_fields / total_fields
        
        # Calculate evidence strength based on scenario type
        if result.basic_info.scenario_type == "PTP" and result.ptp_details:
            if result.ptp_details.promised_date and result.ptp_details.promised_amount:
                metrics["evidence_strength"] = 0.9
        elif result.basic_info.scenario_type == "TPC" and result.tpc_details:
            if result.tpc_details.relationship_to_customer:
                metrics["evidence_strength"] = 0.8
        elif result.basic_info.scenario_type == "REFUSE_TO_PAY" and result.refuse_details:
            if result.refuse_details.reason:
                metrics["evidence_strength"] = 0.8
                
        return metrics
