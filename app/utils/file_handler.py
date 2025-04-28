"""File handling utilities for the application"""
import os
from typing import Optional, List, Dict
import json
from datetime import datetime

class FileHandler:
    """Handles file operations for the application"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file handler
        
        Args:
            base_dir (str, optional): Base directory for file operations
        """
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'data')
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            os.path.join(self.base_dir, 'transcripts'),
            os.path.join(self.base_dir, 'analysis'),
            os.path.join(self.base_dir, 'reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
    def save_transcript(self, content: str, filename: Optional[str] = None) -> str:
        """
        Save transcript content to file
        
        Args:
            content (str): Transcript content
            filename (str, optional): Custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"transcript_{timestamp}.txt"
            
        filepath = os.path.join(self.base_dir, 'transcripts', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath
        
    def save_analysis(self, analysis_data: Dict, transcript_id: str) -> str:
        """
        Save analysis results
        
        Args:
            analysis_data (dict): Analysis results to save
            transcript_id (str): ID of analyzed transcript
            
        Returns:
            str: Path to saved file
        """
        filename = f"analysis_{transcript_id}.json"
        filepath = os.path.join(self.base_dir, 'analysis', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
        return filepath
        
    def save_report(self, report_data: Dict, report_type: str) -> str:
        """
        Save generated report
        
        Args:
            report_data (dict): Report data to save
            report_type (str): Type of report
            
        Returns:
            str: Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_report_{timestamp}.json"
        filepath = os.path.join(self.base_dir, 'reports', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        return filepath
        
    def load_transcript(self, filepath: str) -> Optional[str]:
        """
        Load transcript content
        
        Args:
            filepath (str): Path to transcript file
            
        Returns:
            str: Transcript content or None if file not found
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
            
    def load_analysis(self, analysis_id: str) -> Optional[Dict]:
        """
        Load analysis results
        
        Args:
            analysis_id (str): ID of analysis to load
            
        Returns:
            dict: Analysis data or None if not found
        """
        filepath = os.path.join(self.base_dir, 'analysis', f"analysis_{analysis_id}.json")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
            
    def list_transcripts(self) -> List[Dict[str, str]]:
        """
        List available transcripts
        
        Returns:
            list: List of transcript information
        """
        transcript_dir = os.path.join(self.base_dir, 'transcripts')
        transcripts = []
        
        for filename in os.listdir(transcript_dir):
            filepath = os.path.join(transcript_dir, filename)
            if os.path.isfile(filepath):
                transcripts.append({
                    'id': filename.replace('.txt', ''),
                    'filename': filename,
                    'path': filepath,
                    'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                })
                
        return sorted(transcripts, key=lambda x: x['created'], reverse=True)