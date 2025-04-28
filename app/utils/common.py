"""Common utility functions for the application"""
import re
from typing import Optional, List, Dict
from datetime import datetime

def clean_transcript(text: str) -> str:
    """
    Clean and normalize transcript text
    
    Args:
        text (str): Raw transcript text
        
    Returns:
        str: Cleaned transcript text
    """
    if not text:
        return ""
        
    # Remove timestamp patterns [00:00.000 --> 00:25.460]
    text = re.sub(r'\[\d{2}:\d{2}\.\d{3} -->\s*\d{2}:\d{2}\.\d{3}\]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def extract_call_metadata(text: str) -> Dict[str, str]:
    """
    Extract metadata from transcript text
    
    Args:
        text (str): Transcript text
        
    Returns:
        dict: Extracted metadata
    """
    metadata = {
        "date": None,
        "time": None,
        "duration": None,
        "agent_name": None,
        "customer_name": None
    }
    
    # Try to extract names
    agent_match = re.search(r'saya\s+(\w+)\s+dari BFI', text, re.IGNORECASE)
    if agent_match:
        metadata["agent_name"] = agent_match.group(1)
    
    customer_match = re.search(r'(Bapak|Ibu)\s+(\w+)', text)
    if customer_match:
        metadata["customer_name"] = customer_match.group(2)
    
    return metadata

def extract_amounts(text: str) -> List[Dict[str, any]]:
    """
    Extract monetary amounts from text
    
    Args:
        text (str): Text containing amounts
        
    Returns:
        list: List of extracted amounts with context
    """
    amounts = []
    
    # Pattern for currency amounts (e.g., "Rp 1.234.567" or "1.234.567 rupiah")
    amount_patterns = [
        r'Rp\.?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*rupiah'
    ]
    
    for pattern in amount_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                amount = float(amount_str)
                context = text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
                amounts.append({
                    "value": amount,
                    "currency": "IDR",
                    "context": context.strip()
                })
            except ValueError:
                continue
    
    return amounts

def format_currency(amount: float, currency: str = "IDR") -> str:
    """
    Format currency amount
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code
        
    Returns:
        str: Formatted currency string
    """
    if currency == "IDR":
        return f"Rp {amount:,.2f}"
    return f"{currency} {amount:,.2f}"

def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage safely
    
    Args:
        value (float): Value to calculate percentage for
        total (float): Total value
        
    Returns:
        float: Calculated percentage
    """
    try:
        if total == 0:
            return 0.0
        return (value / total) * 100
    except (TypeError, ZeroDivisionError):
        return 0.0

def parse_date_mentions(text: str) -> List[Dict[str, any]]:
    """
    Extract date mentions from text
    
    Args:
        text (str): Text containing date mentions
        
    Returns:
        list: List of extracted dates with context
    """
    dates = []
    
    # Pattern for date mentions (e.g., "tanggal 8", "besok", "hari ini")
    date_patterns = {
        r'tanggal\s+(\d{1,2})': 'specific_date',
        r'besok': 'tomorrow',
        r'hari\s+ini': 'today',
        r'minggu\s+depan': 'next_week'
    }
    
    for pattern, date_type in date_patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            context = text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
            dates.append({
                "match": match.group(0),
                "type": date_type,
                "specific_date": match.group(1) if date_type == 'specific_date' else None,
                "context": context.strip()
            })
    
    return dates
