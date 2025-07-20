# Job Application Tracker MCP Server

A modular MCP (Model Context Protocol) server that automatically scans your Gmail for job application emails and tracks them in an Excel spreadsheet.

## Project Structure

```
job_application_tracker/
├── __init__.py                    # Package initialization
├── main.py                        # Entry point
├── config/
│   ├── __init__.py
│   └── settings.py               # Configuration settings
├── gmail/
│   ├── __init__.py
│   ├── auth.py                   # Gmail authentication
│   └── email_processor.py       # Email processing logic
├── excel/
│   ├── __init__.py
│   └── tracker.py               # Excel operations
├── classification/
│   ├── __init__.py
│   └── email_classifier.py      # Email classification
├── mcp/
│   ├── __init__.py
│   └── server.py                # MCP server implementation
└── utils/
    ├── __init__.py
    └── logging_config.py         # Logging configuration
```

## Features

- 📧 **Gmail Integration**: Authenticates and searches Gmail using Google API
- 🏢 **Smart Extraction**: Automatically extracts company names and positions
- 🤖 **Email Classification**: Categorizes emails (received, rejection, interview, offer)
- 📊 **Excel Management**: Creates and updates spreadsheets with deduplication
- 🔧 **Modular Design**: Clean separation of concerns with dedicated modules
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ⚙️ **Configurable**: Centralized configuration management

## Architecture

### Core Modules

1. **Gmail Module** (`gmail/`)
   - `auth.py`: Handles OAuth2 authentication with Gmail API
   - `email_processor.py`: Searches and processes email content

2. **Classification Module** (`classification/`)
   - `email_classifier.py`: Classifies emails using regex patterns

3. **Excel Module** (`excel/`)
   - `tracker.py`: Manages Excel file operations and data persistence

4. **MCP Module** (`mcp/`)
   - `server.py`: Implements MCP server with tool definitions

5. **Configuration** (`config/`)
   - `settings.py`: Centralized configuration and constants

6. **Utilities** (`utils/`)
   - `logging_config.py`: Logging setup and management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client ID) for desktop application
5. Download the credentials file as `credentials.json` in the project root

### 3. Configure Claude Desktop

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "job-application-tracker": {
      "command": "python",
      "args": ["-m", "job_application_tracker.main"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### 4. Install as Package (Optional)

```bash
pip install -e .
```

Then you can run:
```bash
job-tracker-mcp
```

## Usage

### Scan for Job Applications

```
scan_job_applications(
    start_date="2024-01-01",
    end_date="2024-12-31", 
    excel_path="my_applications.xlsx"  # optional
)
```

### Get Application Summary

```
get_application_summary(excel_path="my_applications.xlsx")  # optional
```

## Configuration

All configuration is centralized in `config/settings.py`:

```python
class Settings:
    # Gmail API settings
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Excel settings
    DEFAULT_EXCEL_PATH = 'job_applications.xlsx'
    EXCEL_HEADERS = ['Company', 'Position', 'Status', ...]
    
    # Classification patterns
    EMAIL_PATTERNS = {
        'application_received': [...],
        'rejection': [...],
        # ...
    }
```

## Email Classification

The system automatically classifies emails into these categories:

- **application_received**: Confirmation emails when you apply
- **rejection**: Unfortunately, we've decided to move forward with other candidates
- **interview**: Interview invitations and scheduling
- **offer**: Job offers and congratulations
- **unknown**: Emails that don't match known patterns

## Excel Output

The generated Excel file contains these columns:

| Company | Position | Status | Date | Subject | Sender | Message ID | Last Updated |
|---------|----------|--------|------|---------|--------|------------|--------------|

## Extending the System

### Adding New Classification Categories

```python
from job_application_tracker.classification.email_classifier import EmailClassifier

classifier = EmailClassifier()
classifier.add_pattern('follow_up', r'following\s+up\s+on\s+your\s+application')
```

### Custom Excel Processing

```python
from job_application_tracker.excel.tracker import ExcelTracker

tracker = ExcelTracker('custom_path.xlsx')
# Custom processing logic
```

### Custom Email Processing

Extend the `EmailProcessor` class to add custom logic:

```python
from job_application_tracker.gmail.email_processor import EmailProcessor

class CustomEmailProcessor(EmailProcessor):
    def _extract_salary_info(self, body: str) -> str:
        # Custom salary extraction logic
        pass
```

## Logging

Logs are written to both console and `job_tracker.log` file. Configure logging level:

```python
from job_application_tracker.utils.logging_config import setup_logging

setup_logging('DEBUG')  # INFO, WARNING, ERROR
```

## Error Handling

The system includes comprehensive error handling:

- Gmail API authentication failures
- Excel file access issues
- Email parsing errors
- Network connectivity problems

## Security

- Credentials stored locally in `token.json`
- Read-only Gmail access
- No external data transmission
- Local Excel file storage

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Structure

Each module is self-contained with clear interfaces:

- **Single Responsibility**: Each class has one clear purpose
- **Dependency Injection**: Components are loosely coupled
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed logging throughout the system

## Troubleshooting

### Gmail Authentication Issues
- Ensure `credentials.json` is in the project root
- Check Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate if needed

### Excel File Issues
- Ensure write permissions to Excel file location
- Close Excel file before running scans
- Check file path is correct

### Module Import Issues
- Ensure package is installed: `pip install -e .`
- Check Python path includes project directory
- Verify all `__init__.py` files are present

This modular architecture makes the system maintainable, testable, and extensible while providing clear separation of concerns.
