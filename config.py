"""
Configuration for RunningHub API integration
"""

import os

# RunningHub API Configuration
RUNNINGHUB_WEBAPP_ID = os.environ.get("RUNNINGHUB_WEBAPP_ID", "")
RUNNINGHUB_API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "")

# Node IDs for different operations
NODE_IDS = {
    "text_to_image": "1",
    "image_enhancer": "2",
    "image_to_image": "3",
    "image_to_video": "4"
}

# Default timeout and polling settings
DEFAULT_TIMEOUT = 600  # 10 minutes
DEFAULT_POLL_INTERVAL = 3  # 3 seconds


def validate_credentials():
    """Validate that required credentials are set"""
    if not RUNNINGHUB_WEBAPP_ID or not RUNNINGHUB_API_KEY:
        raise ValueError(
            "RunningHub credentials not configured. Please set the following environment variables:\n"
            "  RUNNINGHUB_WEBAPP_ID\n"
            "  RUNNINGHUB_API_KEY\n"
            "\nYou can get these credentials from https://www.runninghub.cn"
        )
