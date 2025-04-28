# analyzer.py
import os
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from .models import SimpleAnalysis, PaymentPromise, Recommendation, CustomerInfo
from .processor import SimpleCollectionProcessor

class AnalysisOutput(BaseModel):
    recommendations: List[Recommendation]
    summary: str

class SimpleCollectionAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("MODEL_STUDIO_API_KEY"),
            model="qwen-plus",
            base_url=os.getenv("MODEL_STUDIO_BASE_URL"),
            temperature=0.0,
        )
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Anda adalah analis collection yang ahli untuk perusahaan pembiayaan di Indonesia.
                Analisis detail nasabah dan janji bayar yang diberikan, lalu berikan rekomendasi.

                Perhatikan:
                1. Informasi dasar nasabah
                2. Ada tidaknya janji bayar yang jelas
                3. Kejelasan tanggal dan jumlah yang dijanjikan
                4. Tingkat keyakinan janji bayar
                5. Praktik collection terbaik
                6. Konteks collection di Indonesia

                Kembalikan analisis dalam format JSON:
                {{
                    "recommendations": [
                        {{
                            "action": "tindakan yang direkomendasikan",
                            "priority": "tinggi/sedang/rendah",
                            "reason": "alasan rekomendasi"
                        }}
                    ],
                    "summary": "ringkasan analisis"
                }}

                Pastikan:
                - Rekomendasi spesifik dan dapat ditindaklanjuti
                - Ringkasan jelas dan singkat
                - Gunakan Bahasa Indonesia yang formal
                - Prioritaskan tindakan berdasarkan urgensi
                """
            ),
            ("human", "Analisis informasi berikut:\n{case_details}")
        ])
        
        # Create analysis chain
        self.analyzer = (
            self.analysis_prompt 
            | self.llm.with_structured_output(AnalysisOutput)
        )
        
        self.processor = SimpleCollectionProcessor()

    def analyze_chat(self, file_path: str) -> SimpleAnalysis:
        """Analyze chat file and return recommendations in Indonesian."""
        try:
            # Get customer info and payment promise analysis
            customer_info, promise = self.processor.process_chat(file_path)
            
            # Prepare case details for analysis
            case_details = {
                "customer_info": {
                    "name": customer_info.name,
                    "agreement_number": customer_info.agreement_number,
                    "product": customer_info.product,
                    "overdue_amount": customer_info.overdue_amount
                },
                "payment_promise": {
                    "has_promise": promise.has_promise,
                    "promise_date": promise.promise_date.isoformat() if promise.promise_date else None,
                    "promise_amount": promise.promise_amount,
                    "confidence_score": promise.confidence_score,
                    "promise_messages": promise.promise_messages
                }
            }
            
            # Get recommendations and summary using LLM
            analysis_output = self.analyzer.invoke({"case_details": str(case_details)})
            
            # Combine results
            return SimpleAnalysis(
                customer_info=customer_info,
                payment_promise=promise,
                recommendations=analysis_output.recommendations,
                summary=analysis_output.summary
            )
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise ValueError(f"Error analyzing chat: {str(e)}")