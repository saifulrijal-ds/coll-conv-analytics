"""Contains prompt templates for LLM analysis"""

CLASSIFICATION_PROMPT = """You are an expert collection call analyzer focusing on Indonesian language transcripts. Your primary task is to accurately classify and extract information from collection call transcripts.

Analyze this call transcript and categorize it into one of these scenarios:

1. PTP (Promise to Pay):
- Customer explicitly provides a specific payment date
- Must be a direct promise from customer (not a guess or suggestion from agent)
Examples:
- "Iya, saya bayar tanggal 8" (PTP)
- "Besok saya bayar" (PTP)
- "Insya Allah tanggal 27" (PTP)

2. Third Party Contact (TPC):
- Person answering is neither customer nor spouse
- Focus on relationship verification
- Message delivery tracking
Examples:
- "Saya adiknya"
- "Beliau sedang tidak ada"
- "Nanti saya sampaikan"

3. Refuse to Pay:
- No clear PTP date given
- Contact is with actual customer (not TPC)
- Expressing inability or unwillingness to pay
Examples:
- "Belum ada uang"
- "Saya tidak sanggup bayar"
- "Mau dikembalikan unitnya"

Call Transcript to analyze:
{text}

Provide a structured analysis including:
- Identified scenario type
- Reason for classification
- Key evidence from transcript
- Any amounts or dates mentioned
- Agent and customer names if available"""

QA_SCORING_PROMPT = """You are an expert QA analyst for collection call centers, specializing in evaluating agent performance based on strict QA criteria. Your task is to analyze a call transcript and extract detailed scoring information.

Context: The call has already been classified as {scenario_type}. You will evaluate the call based on the appropriate QA form criteria for this scenario type.

Required Output Format:
The output should be a JSON object matching the following structure example:
{{
    "scenario_type": "{scenario_type}",
    "opening_score": {{
        "greeting_score": "0|0.5|1",
        "greeting_evidence": "exact quote from transcript",
        "customer_name_verification": "COMPLIANT|NON_COMPLIANT|NOT_APPLICABLE",
        "customer_verification_evidence": "exact quote or null",
        "mandatory_info_disclosed": ["list of disclosed items"]
    }},
    "communication_score": {{
        "voice_tone_score": "0|0.5|1",
        "voice_tone_evidence": "evidence or null",
        "speaking_pace_score": "0|0.5|1",
        "speaking_pace_evidence": "evidence or null",
        "language_etiquette_score": "0|0.5|1",
        "language_evidence": ["examples"]
    }},
    "negotiation_score": {{
        "negotiation_attempts": number,
        "solutions_offered": ["list of solutions"],
        "payment_commitment_obtained": boolean,
        "negotiation_evidence": ["key phrases"]
    }},
    "knockout_violations": {{
        "unauthorized_disclosure": boolean,
        "disclosure_evidence": "evidence or null",
        "ptp_cheating": boolean,
        "ptp_cheating_evidence": "evidence or null",
        "other_violations": ["list of violations"]
    }},
    "total_score": number between 0-1,
    "score_breakdown": {{
        "opening": number,
        "communication": number,
        "negotiation": number
    }},
    "improvement_areas": ["list of areas"],
    "evidence_highlights": ["list of key evidence"]
}}

Evaluation Guidelines:

1. Opening Section (6% weight):
- Listen for proper greeting, agent name, and company name
- Verify correct customer name usage
- Check for mandatory information disclosure
- Score: 0 (non-compliant), 0.5 (standard), 1 (strong)

2. Communication Skills (25% total weight):
- Voice tone (6%): Energy, professionalism, confidence
- Speaking pace (6%): Clear articulation, appropriate speed
- Language etiquette (13%): Politeness, appropriate phrases
- Score each component: 0 (poor), 0.5 (acceptable), 1 (excellent)

3. Negotiation Skills (40% total weight, for PTP/RTP):
- Track negotiation attempts
- Document solutions offered
- Verify payment commitments
- Evaluate effectiveness: 0 (ineffective), 0.5 (moderate), 1 (highly effective)

4. Knockout Criteria (Immediate Fail):
- Information disclosure to unauthorized parties
- PTP cheating
- Policy violations
- Document any violations with specific evidence

Call Transcript to analyze:
{text}

Analyze the transcript and provide a complete evaluation following the exact structure shown above."""

def get_scenario_specific_additions(scenario_type: str) -> str:
    """Get scenario-specific scoring criteria"""
    
    additions = {
        "PTP": """
Additional PTP Criteria:
- Focus on commitment clarity
- Verify payment amount and date
- Check for proper confirmation
- Evaluate follow-up scheduling""",
        
        "REFUSE_TO_PAY": """
Additional RTP Criteria:
- Evaluate reason documentation
- Check solution exploration
- Assess escalation handling
- Monitor professional persistence""",
        
        "TPC": """
Additional TPC Criteria:
- Verify relationship confirmation
- Check information protection
- Evaluate message clarity
- Assess contact information gathering"""
    }
    
    return additions.get(scenario_type, "")
