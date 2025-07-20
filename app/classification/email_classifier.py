"""Email classification functionality"""

import re
from typing import Dict, List

from job_application_tracker.config.settings import Settings
from job_application_tracker.utils.logging_config import get_logger

logger = get_logger(__name__)

class EmailClassifier:
    """Classifies emails based on content patterns"""
    
    def __init__(self):
        self.patterns = Settings.EMAIL_PATTERNS
    
    def classify_email(self, subject: str, body: str) -> str:
        """Classify email based on content"""
        content = f"{subject} {body}".lower()
        
        # Check each category
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.debug(f"Email classified as '{category}' based on pattern: {pattern}")
                    return category
        
        logger.debug("Email could not be classified, returning 'unknown'")
        return 'unknown'
    
    def classify_applications(self, applications: List[Dict]) -> List[Dict]:
        """Classify a list of applications"""
        for application in applications:
            application['status'] = self.classify_email(
                application['subject'], 
                application.get('body', '')
            )
        
        return applications
    
    def add_pattern(self, category: str, pattern: str) -> None:
        """Add a new classification pattern"""
        if category not in self.patterns:
            self.patterns[category] = []
        self.patterns[category].append(pattern)
        logger.info(f"Added pattern '{pattern}' to category '{category}'")
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self.patterns.keys())