"""Database handling utilities for the application"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

class DatabaseHandler:
    """Handles database operations for the application"""
    
    def __init__(self, db_path: str = "data/analysis.db"):
        """
        Initialize database handler
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()
        
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    transcript_text TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    qa_score REAL NOT NULL,
                    classification_data TEXT NOT NULL,
                    qa_data TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create issues table for tracking critical issues
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS critical_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER NOT NULL,
                    issue_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    evidence TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                )
            """)
            
            conn.commit()
            
    def save_analysis(self, 
                     transcript: str,
                     classification_data: Dict,
                     qa_data: Dict,
                     metadata: Optional[Dict] = None) -> int:
        """
        Save analysis results to database
        
        Args:
            transcript (str): Original transcript text
            classification_data (dict): Classification results
            qa_data (dict): QA scoring results
            metadata (dict, optional): Additional metadata
            
        Returns:
            int: ID of saved analysis
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main analysis record
            cursor.execute("""
                INSERT INTO analyses (
                    timestamp,
                    transcript_text,
                    scenario_type,
                    qa_score,
                    classification_data,
                    qa_data,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                transcript,
                classification_data["basic_info"]["scenario_type"],
                qa_data["total_score"],
                json.dumps(classification_data),
                json.dumps(qa_data),
                json.dumps(metadata) if metadata else None
            ))
            
            analysis_id = cursor.lastrowid
            
            # Save critical issues if any
            if qa_data.get("knockout_violations"):
                for violation in qa_data["knockout_violations"].get("other_violations", []):
                    cursor.execute("""
                        INSERT INTO critical_issues (
                            analysis_id,
                            issue_type,
                            description,
                            evidence
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        analysis_id,
                        "violation",
                        violation,
                        None
                    ))
            
            conn.commit()
            return analysis_id
            
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """
        Retrieve analysis by ID
        
        Args:
            analysis_id (int): ID of analysis to retrieve
            
        Returns:
            dict: Analysis data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    timestamp,
                    transcript_text,
                    scenario_type,
                    qa_score,
                    classification_data,
                    qa_data,
                    metadata
                FROM analyses
                WHERE id = ?
            """, (analysis_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return {
                "id": row[0],
                "timestamp": row[1],
                "transcript": row[2],
                "scenario_type": row[3],
                "qa_score": row[4],
                "classification_data": json.loads(row[5]),
                "qa_data": json.loads(row[6]),
                "metadata": json.loads(row[7]) if row[7] else None
            }
            
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """
        Get recent analyses
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of recent analyses
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    timestamp,
                    scenario_type,
                    qa_score
                FROM analyses
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [{
                "id": row[0],
                "timestamp": row[1],
                "scenario_type": row[2],
                "qa_score": row[3]
            } for row in cursor.fetchall()]
            
    def get_statistics(self) -> Dict:
        """
        Get analysis statistics
        
        Returns:
            dict: Statistical information about analyses
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(qa_score) as avg_score,
                    COUNT(CASE WHEN qa_score >= 0.85 THEN 1 END) as passing
                FROM analyses
            """)
            
            total, avg_score, passing = cursor.fetchone()
            
            # Get scenario distribution
            cursor.execute("""
                SELECT 
                    scenario_type,
                    COUNT(*) as count
                FROM analyses
                GROUP BY scenario_type
            """)
            
            scenarios = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_analyses": total,
                "average_score": avg_score,
                "passing_rate": (passing / total) if total > 0 else 0,
                "scenario_distribution": scenarios
            }
            
    def export_analysis(self, analysis_id: int, filepath: str):
        """
        Export analysis to file
        
        Args:
            analysis_id (int): ID of analysis to export
            filepath (str): Path to save exported file
        """
        analysis = self.get_analysis(analysis_id)
        if analysis:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

# Create global database handler instance
db = DatabaseHandler()
