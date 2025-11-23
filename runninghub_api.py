"""
RunningHub API Client for ComfyUI
Provides interface to RunningHub's AI generation services
"""

import requests
import time
import json
from typing import Dict, Optional, Tuple, Any


class RunningHubAPI:
    """Client for interacting with RunningHub API"""

    BASE_URL = "https://www.runninghub.cn"

    def __init__(self, webapp_id: str, api_key: str):
        """
        Initialize RunningHub API client

        Args:
            webapp_id: Your RunningHub webapp ID
            api_key: Your RunningHub API key
        """
        self.webapp_id = webapp_id
        self.api_key = api_key

    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to RunningHub

        Args:
            image_path: Path to the image file

        Returns:
            File ID from RunningHub
        """
        url = f"{self.BASE_URL}/task/openapi/upload"

        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'apiKey': self.api_key}

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            if result.get('code') == 0:
                return result['data']['fileId']
            else:
                raise Exception(f"Upload failed: {result.get('msg', 'Unknown error')}")

    def submit_task(self, node_id: str, node_info_list: list) -> str:
        """
        Submit a task to RunningHub

        Args:
            node_id: The node ID for the operation type
            node_info_list: List of node parameters

        Returns:
            Task ID for polling
        """
        url = f"{self.BASE_URL}/task/openapi/ai-app/run"

        payload = {
            "webappId": self.webapp_id,
            "apiKey": self.api_key,
            "nodeInfoList": [{
                "nodeId": node_id,
                "nodeInfoList": node_info_list
            }]
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get('code') == 0:
            return result['data']['id']
        else:
            raise Exception(f"Task submission failed: {result.get('msg', 'Unknown error')}")

    def check_task_status(self, task_id: str) -> Tuple[str, int]:
        """
        Check the status of a task

        Args:
            task_id: The task ID to check

        Returns:
            Tuple of (status, progress_percentage)
            Status can be: RUNNING, SUCCESS, FAILED, PENDING
        """
        url = f"{self.BASE_URL}/task/openapi/status"

        payload = {
            "apiKey": self.api_key,
            "id": task_id
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get('code') != 0:
            raise Exception(f"Status check failed: {result.get('msg', 'Unknown error')}")

        data = result.get('data', {})
        status = data.get('status', 'UNKNOWN').upper()

        # Normalize status strings
        if status in ['SUCCESS', 'COMPLETED']:
            status = 'SUCCESS'
        elif status in ['RUNNING', 'PROCESSING']:
            status = 'RUNNING'
        elif status in ['FAILED', 'ERROR']:
            status = 'FAILED'
        elif status in ['PENDING', 'QUEUED']:
            status = 'PENDING'

        # Get progress percentage
        progress = data.get('progress', 0)
        if isinstance(progress, str):
            try:
                progress = int(progress.replace('%', ''))
            except:
                progress = 0 if status == 'PENDING' else 50 if status == 'RUNNING' else 100

        return status, progress

    def get_task_result(self, task_id: str) -> list:
        """
        Get the result URLs from a completed task

        Args:
            task_id: The task ID

        Returns:
            List of output file URLs
        """
        url = f"{self.BASE_URL}/task/openapi/outputs"

        payload = {
            "apiKey": self.api_key,
            "id": task_id
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get('code') != 0:
            raise Exception(f"Result retrieval failed: {result.get('msg', 'Unknown error')}")

        data = result.get('data', [])
        urls = []

        for item in data:
            if isinstance(item, dict) and 'url' in item:
                urls.append(item['url'])
            elif isinstance(item, str):
                urls.append(item)

        return urls

    def wait_for_task(self, task_id: str, timeout: int = 600, poll_interval: int = 3) -> list:
        """
        Wait for a task to complete and return results

        Args:
            task_id: The task ID to wait for
            timeout: Maximum time to wait in seconds (default: 600 = 10 minutes)
            poll_interval: Seconds between status checks (default: 3)

        Returns:
            List of output file URLs
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status, progress = self.check_task_status(task_id)

            print(f"Task {task_id}: {status} ({progress}%)")

            if status == 'SUCCESS':
                return self.get_task_result(task_id)
            elif status == 'FAILED':
                raise Exception(f"Task {task_id} failed")

            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
