"""Gmail email processing functionality"""

import base64
import re
from datetime import datetime
from typing import Dict, List, Any

from googleapiclient.errors import HttpError

from job_application_tracker.config.settings import Settings
from job_application_tracker.gmail.auth import GmailAuthenticator
from job_application_tracker.utils.logging_config import get_logger

logger = get_logger(__name__)

class EmailProcessor:
    """Processes Gmail emails for job application tracking"""
    
    def __init__(self, authenticator: GmailAuthenticator):
        self.authenticator = authenticator
    
    async def search_application_emails(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Search Gmail for job application related emails"""
        if not self.authenticator.is_authenticated:
            if not await self.authenticator.authenticate():
                return []
        
        try:
            # Convert dates to Gmail search format
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Build Gmail search query
            query = self._build_search_query(start_dt, end_dt)
            logger.info(f"Searching Gmail with query: {query}")
            
            # Search for messages
            results = self.authenticator.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=Settings.MAX_SEARCH_RESULTS
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} potential job application emails")
            
            applications = []
            
            for message in messages:
                try:
                    application = await self._process_message(message['id'])
                    if application:
                        applications.append(application)
                        logger.info(f"Processed: {application['company']} - {application['status']}")
                        
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return applications
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
    
    def _build_search_query(self, start_dt: datetime, end_dt: datetime) -> str:
        """Build Gmail search query"""
        query_terms = Settings.SEARCH_TERMS
        date_range = f"after:{start_dt.strftime('%Y/%m/%d')} before:{end_dt.strftime('%Y/%m/%d')}"
        return f"({' OR '.join(query_terms)}) {date_range}"
    
    async def _process_message(self, message_id: str) -> Dict[str, Any]:
        """Process a single Gmail message"""
        # Get full message details
        msg = self.authenticator.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = msg['payload'].get('headers', [])
        subject = self._get_header_value(headers, 'Subject')
        sender = self._get_header_value(headers, 'From')
        date_header = self._get_header_value(headers, 'Date')
        
        # Extract body
        body = self._extract_email_body(msg['payload'])
        
        # Extract company and position info
        company_info = self._extract_company_info(sender, subject, body)
        
        # Parse date
        email_date_str = self._parse_email_date(date_header)
        
        return {
            'company': company_info['company'],
            'position': company_info['position'],
            'status': 'unknown',  # Will be classified later
            'date': email_date_str,
            'subject': subject,
            'sender': sender,
            'body': body,
            'message_id': message_id
        }
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Get header value by name"""
        return next((h['value'] for h in headers if h['name'] == name), '')
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extract text body from email payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'multipart/alternative':
                    body += self._extract_email_body(part)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def _extract_company_info(self, sender: str, subject: str, body: str) -> Dict[str, str]:
        """Extract company name and position from email"""
        # Extract company from sender email domain
        company = "Unknown"
        if '@' in sender:
            domain = sender.split('@')[1].lower()
            # Remove common email providers
            if domain not in Settings.COMMON_EMAIL_PROVIDERS:
                company = domain.split('.')[0].title()
        
        # Try to extract position from subject
        position = self._extract_position(subject)
        
        return {
            'company': company,
            'position': position
        }
    
    def _extract_position(self, subject: str) -> str:
        """Extract position from email subject"""
        position = "Unknown"
        
        # Common position patterns in subjects
        position_patterns = [
            r'(?:for\s+(?:the\s+)?)?(?:position\s+of\s+)?([a-zA-Z\s]+?)(?:\s+position|\s+role|\s+at|\s+-)',
            r'(?:role:\s*|position:\s*)([a-zA-Z\s]+)',
            r'application\s+for\s+([a-zA-Z\s]+?)(?:\s+at|\s+-|\s+position)',
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                position = match.group(1).strip().title()
                break
        
        return position
    
    def _parse_email_date(self, date_header: str) -> str:
        """Parse email date header"""
        try:
            email_date = datetime.strptime(
                date_header.split(' (')[0], 
                '%a, %d %b %Y %H:%M:%S %z'
            )
            return email_date.strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')
