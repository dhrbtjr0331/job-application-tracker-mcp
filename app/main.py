"""Main entry point for the Job Application Tracker MCP Server"""

import asyncio
from job_application_tracker.mcp.server import create_server
from job_application_tracker.utils.logging_config import setup_logging

async def main():
    """Main entry point"""
    setup_logging()
    server = create_server()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())