"""MCP server implementation for job application tracking"""

import asyncio
from typing import List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from job_application_tracker.gmail.auth import GmailAuthenticator
from job_application_tracker.gmail.email_processor import EmailProcessor
from job_application_tracker.classification.email_classifier import EmailClassifier
from job_application_tracker.excel.tracker import ExcelTracker
from job_application_tracker.utils.logging_config import get_logger

logger = get_logger(__name__)

class JobApplicationMCPServer:
    """MCP Server for job application tracking"""
    
    def __init__(self):
        self.server = Server("job-application-tracker")
        self.authenticator = GmailAuthenticator()
        self.email_processor = EmailProcessor(self.authenticator)
        self.classifier = EmailClassifier()
        self.excel_tracker = ExcelTracker()
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="scan_job_applications",
                    description="Scan Gmail for job application emails and update Excel tracker",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "format": "date",
                                "description": "Start date for email search (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "type": "string", 
                                "format": "date",
                                "description": "End date for email search (YYYY-MM-DD)"
                            },
                            "excel_path": {
                                "type": "string",
                                "description": "Path to Excel file (optional, defaults to job_applications.xlsx)"
                            }
                        },
                        "required": ["start_date", "end_date"]
                    }
                ),
                types.Tool(
                    name="get_application_summary",
                    description="Get summary of tracked applications from Excel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "excel_path": {
                                "type": "string",
                                "description": "Path to Excel file (optional)"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls"""
            
            if name == "scan_job_applications":
                return await self._handle_scan_applications(arguments)
            elif name == "get_application_summary":
                return await self._handle_get_summary(arguments)
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def _handle_scan_applications(self, arguments: dict) -> List[types.TextContent]:
        """Handle scan job applications tool call"""
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        excel_path = arguments.get("excel_path")
        
        try:
            # Update excel tracker path if provided
            if excel_path:
                self.excel_tracker = ExcelTracker(excel_path)
            
            # Search for applications
            applications = await self.email_processor.search_application_emails(start_date, end_date)
            
            if not applications:
                return [types.TextContent(
                    type="text",
                    text="No job application emails found in the specified date range."
                )]
            
            # Classify applications
            applications = self.classifier.classify_applications(applications)
            
            # Update Excel
            success = self.excel_tracker.update_applications(applications)
            
            if success:
                summary = self._generate_scan_summary(applications)
                return [types.TextContent(type="text", text=summary)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Found applications but failed to update Excel file."
                )]
                
        except Exception as e:
            logger.error(f"Error in scan_job_applications: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error scanning applications: {str(e)}"
            )]
    
    async def _handle_get_summary(self, arguments: dict) -> List[types.TextContent]:
        """Handle get application summary tool call"""
        excel_path = arguments.get("excel_path")
        
        try:
            if excel_path:
                excel_tracker = ExcelTracker(excel_path)
            else:
                excel_tracker = self.excel_tracker
            
            summary_data = excel_tracker.get_application_summary()
            
            if "error" in summary_data:
                return [types.TextContent(
                    type="text",
                    text=summary_data["error"]
                )]
            
            summary = self._generate_summary_text(summary_data)
            return [types.TextContent(type="text", text=summary)]
            
        except Exception as e:
            logger.error(f"Error in get_application_summary: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error reading Excel file: {str(e)}"
            )]
    
    def _generate_scan_summary(self, applications: List[dict]) -> str:
        """Generate summary text for scan results"""
        status_counts = {}
        for app in applications:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        summary = f"Successfully processed {len(applications)} job application emails:\n\n"
        for status, count in status_counts.items():
            summary += f"• {status.title()}: {count}\n"
        
        summary += f"\nData saved to: {self.excel_tracker.excel_path}"
        return summary
    
    def _generate_summary_text(self, summary_data: dict) -> str:
        """Generate summary text from summary data"""
        total = summary_data["total_applications"]
        status_counts = summary_data["status_counts"]
        
        summary = f"Application Summary (Total: {total}):\n\n"
        for status, count in status_counts.items():
            percentage = (count / total) * 100
            summary += f"• {status.title()}: {count} ({percentage:.1f}%)\n"
        
        return summary
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="job-application-tracker",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

def create_server() -> JobApplicationMCPServer:
    """Create and return a new MCP server instance"""
    return JobApplicationMCPServer()