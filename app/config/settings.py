"""Configuration settings for the job application tracker"""

from pathlib import Path
from typing import List

class Settings:
    """Application settings"""
    
    # Gmail API settings
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    # Default Excel file path
    DEFAULT_EXCEL_PATH = 'job_applications.xlsx'
    DEFAULT_SHEET_NAME = 'Applications'
    
    # Email search settings
    MAX_SEARCH_RESULTS = 100
    
    # Excel column headers
    EXCEL_HEADERS = [
        'Company', 'Position', 'Status', 'Date', 
        'Subject', 'Sender', 'Message ID', 'Last Updated'
    ]
    
    # Email classification patterns
    EMAIL_PATTERNS = {
        'application_received': [
            r'thank\s+you\s+for\s+(?:your\s+)?(?:interest|applying)',
            r'application\s+(?:has\s+been\s+)?received',
            r'we\s+have\s+received\s+your\s+application',
            r'your\s+application\s+for',
            r'application\s+confirmation'
        ],
        'rejection': [
            r'unfortunately',
            r'we\s+regret\s+to\s+inform',
            r'after\s+careful\s+consideration',
            r'we\s+have\s+decided\s+to\s+move\s+forward\s+with\s+other',
            r'not\s+selected\s+for\s+(?:this\s+)?position',
            r'we\s+will\s+not\s+be\s+moving\s+forward',
            r'position\s+has\s+been\s+filled'
        ],
        'interview': [
            r'interview',
            r'schedule\s+(?:a\s+)?(?:call|meeting)',
            r'next\s+(?:step|round)',
            r'would\s+like\s+to\s+(?:speak|talk)\s+with\s+you',
            r'phone\s+(?:screen|call)',
            r'video\s+(?:call|interview)'
        ],
        'offer': [
            r'pleased\s+to\s+(?:offer|extend)',
            r'job\s+offer',
            r'offer\s+of\s+employment',
            r'congratulations',
            r'we\s+would\s+like\s+to\s+offer\s+you'
        ]
    }
    
    # Gmail search terms
    SEARCH_TERMS = [
        '"thanks for applying"',
        '"application received"',
        '"thank you for your interest"',
        '"unfortunately"',
        '"interview"',
        '"job offer"',
        '"application confirmation"',
        '"we have received your application"'
    ]
    
    # Email providers to exclude from company extraction
    COMMON_EMAIL_PROVIDERS = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'icloud.com', 'aol.com', 'protonmail.com'
    ]
