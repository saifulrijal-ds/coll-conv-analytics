# models.py
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CustomerInfo(BaseModel):
    """Basic customer information"""
    name: Optional[str] = Field(default=None, description="Nama nasabah")
    agreement_number: Optional[str] = Field(default=None, description="Nomor perjanjian")
    product: Optional[str] = Field(default=None, description="Jenis produk")
    overdue_amount: Optional[float] = Field(default=None, description="Jumlah tunggakan")

class PaymentPromise(BaseModel):
    """Payment promise details"""
    has_promise: bool = Field(..., description="Ada janji bayar atau tidak")
    promise_date: Optional[datetime] = Field(default=None, description="Tanggal janji bayar")
    promise_amount: Optional[float] = Field(default=None, description="Jumlah janji bayar")
    confidence_score: float = Field(..., description="Tingkat keyakinan deteksi janji")
    promise_messages: List[str] = Field(default_factory=list, description="Pesan yang berisi janji")

class Recommendation(BaseModel):
    """Recommended action"""
    action: str = Field(..., description="Rekomendasi tindakan")
    priority: str = Field(..., description="Prioritas (tinggi/sedang/rendah)")
    reason: str = Field(..., description="Alasan rekomendasi")

class SimpleAnalysis(BaseModel):
    """Simplified collection chat analysis"""
    customer_info: CustomerInfo = Field(..., description="Informasi nasabah")
    payment_promise: PaymentPromise = Field(..., description="Detail janji bayar")
    recommendations: List[Recommendation] = Field(..., description="Rekomendasi tindakan")
    summary: str = Field(..., description="Ringkasan analisis")