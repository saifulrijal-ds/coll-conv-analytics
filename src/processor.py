# processor.py
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from .models import PaymentPromise, CustomerInfo

class ChatMessage(BaseModel):
    """Individual chat message"""
    timestamp: str = Field(..., description="Message timestamp")
    role: str = Field(..., description="Role of the sender (agent/customer/system)")
    content: str = Field(..., description="Message content")

class ChatHistory(BaseModel):
    """Parsed chat history"""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")

class SimpleCollectionProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("MODEL_STUDIO_API_KEY"),
            model="qwen-plus",
            base_url=os.getenv("MODEL_STUDIO_BASE_URL"),
            temperature=0.0,
        )
        
        # Customer info extraction prompt
        self.customer_info_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Anda adalah sistem ekstraksi informasi yang spesialis dalam percakapan collection.
                Analisa percakapan untuk menemukan informasi nasabah berikut:

                1. Nama nasabah
                2. Nomor perjanjian
                3. Jenis produk (jika ada)
                4. Jumlah tunggakan (jika disebutkan)

                Kembalikan dalam format JSON:
                {{
                    "name": "string atau null",
                    "agreement_number": "string atau null",
                    "product": "string atau null",
                    "overdue_amount": number atau null
                }}

                Catatan:
                - Jika informasi tidak ditemukan, isi dengan null
                - Untuk jumlah tunggakan, hilangkan 'Rp' dan tanda koma
                - Perhatikan berbagai format penulisan nomor perjanjian
                """
            ),
            ("human", "{messages}")
        ])

        # Promise detection prompt
        self.promise_detection_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Anda adalah sistem analisis janji bayar yang spesialis dalam percakapan collection.
                Analisa percakapan untuk menemukan janji pembayaran.

                Perhatikan:
                1. Deteksi janji bayar dalam Bahasa Indonesia
                2. Ekstrak tanggal janji bayar
                3. Ekstrak jumlah yang dijanjikan
                
                Frasa janji bayar umum:
                - "janji bayar"
                - "akan bayar"
                - "bisa bayar"
                - "bayar tanggal"
                - "tanggal ... saya bayar"
                - "nanti saya bayar"

                Kembalikan dalam format JSON:
                {{
                    "has_promise": true/false,
                    "promise_date": "YYYY-MM-DD" atau null,
                    "promise_amount": number atau null,
                    "confidence_score": 0.0-1.0,
                    "promise_messages": ["pesan1", "pesan2"]
                }}

                Format:
                - Tanggal dalam YYYY-MM-DD
                - Jumlah tanpa 'Rp' dan tanda koma
                - Confidence score: 1.0 = sangat yakin, 0.0 = tidak ada janji
                """
            ),
            ("human", "{messages}")
        ])
        
        # Create the chains
        self.chat_parser = (
            ChatPromptTemplate.from_messages([
                ("system", "Parse the chat log into messages. Return in format: {{\"messages\": [...]}}"),
                ("human", "{raw_content}")
            ])
            | self.llm.with_structured_output(ChatHistory)
        )
        
        self.customer_info_extractor = (
            self.customer_info_prompt 
            | self.llm.with_structured_output(CustomerInfo)
        )
        
        self.promise_detector = (
            self.promise_detection_prompt 
            | self.llm.with_structured_output(PaymentPromise)
        )

    def process_chat(self, file_path: str) -> Tuple[CustomerInfo, PaymentPromise]:
        """Process chat file and extract customer info and payment promises."""
        try:
            # Read raw file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='cp1252') as f:
                    raw_content = f.read()

            # Parse chat messages
            chat_history = self.chat_parser.invoke({"raw_content": raw_content})
            
            # Format messages for analysis
            messages_text = "\n".join([
                f"[{msg.timestamp}] {msg.role}: {msg.content}"
                for msg in chat_history.messages
            ])
            
            # Extract customer info
            customer_info = self.customer_info_extractor.invoke({"messages": messages_text})
            
            # Detect payment promises
            promise_analysis = self.promise_detector.invoke({"messages": messages_text})
            
            return customer_info, promise_analysis
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise ValueError(f"Error processing chat: {str(e)}")