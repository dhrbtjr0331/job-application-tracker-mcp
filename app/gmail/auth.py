"""Gmail authentication handling"""

from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from job_application_tracker.config.settings import Settings
from job_application_tracker.utils.logging_config import get_logger

logger = get_logger(__name__)

class GmailAuthenticator:
    """Handles Gmail API authentication"""
    
    def __init__(self):
        self.scopes = Settings.GMAIL_SCOPES
        self.credentials_path = Path(Settings.CREDENTIALS_FILE)
        self.token_path = Path(Settings.TOKEN_FILE)
        self._service = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), self.scopes
                )
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path.exists():
                        logger.error(
                            f"Credentials file not found: {self.credentials_path}. "
                            "Please download from Google Cloud Console."
                        )
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self._service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False
    
    @property
    def service(self):
        """Get the Gmail service instance"""
        return self._service
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        return self._service is not None
