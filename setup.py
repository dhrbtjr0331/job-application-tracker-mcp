from setuptools import setup, find_packages

setup(
    name="job-application-tracker-mcp",
    version="1.0.0",
    description="MCP server for tracking job applications from Gmail to Excel",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=1.0.0", 
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "job-tracker-mcp=job_application_tracker.main:main",
        ],
    },
)