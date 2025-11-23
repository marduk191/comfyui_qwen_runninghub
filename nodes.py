"""
ComfyUI Nodes for RunningHub API Integration
"""

import os
import torch
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import folder_paths
import hashlib

from .runninghub_api import RunningHubAPI
from .config import (
    RUNNINGHUB_WEBAPP_ID,
    RUNNINGHUB_API_KEY,
    NODE_IDS,
    DEFAULT_TIMEOUT,
    DEFAULT_POLL_INTERVAL,
    validate_credentials
)


class RunningHubTextToImage:
    """Generate images from text prompts using RunningHub API"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful landscape"
                }),
                "webapp_id": ("STRING", {
                    "default": RUNNINGHUB_WEBAPP_ID
                }),
                "api_key": ("STRING", {
                    "default": RUNNINGHUB_API_KEY
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "timeout": ("INT", {
                    "default": DEFAULT_TIMEOUT,
                    "min": 60,
                    "max": 1800
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "RunningHub"

    def generate(self, prompt, webapp_id, api_key, negative_prompt="", timeout=DEFAULT_TIMEOUT):
        """Generate image from text prompt"""

        if not webapp_id or not api_key:
            raise ValueError("RunningHub credentials are required")

        api = RunningHubAPI(webapp_id, api_key)

        # Prepare node info
        node_info = [
            {
                "fieldName": "prompt",
                "fieldValue": prompt,
                "description": "Text prompt for image generation"
            }
        ]

        if negative_prompt:
            node_info.append({
                "fieldName": "negative_prompt",
                "fieldValue": negative_prompt,
                "description": "Negative prompt"
            })

        print(f"Submitting text-to-image task with prompt: {prompt[:50]}...")

        # Submit task
        task_id = api.submit_task(NODE_IDS["text_to_image"], node_info)
        print(f"Task submitted: {task_id}")

        # Wait for result
        result_urls = api.wait_for_task(task_id, timeout=timeout)

        if not result_urls:
            raise Exception("No images generated")

        # Download and convert first image to ComfyUI format
        image_url = result_urls[0]
        print(f"Downloading image from: {image_url}")

        response = requests.get(image_url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")

        # Convert to tensor format expected by ComfyUI
        image_np = np.array(image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        return (image_tensor,)


class RunningHubImageToImage:
    """Transform images with text prompts using RunningHub API"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Transform this image"
                }),
                "webapp_id": ("STRING", {
                    "default": RUNNINGHUB_WEBAPP_ID
                }),
                "api_key": ("STRING", {
                    "default": RUNNINGHUB_API_KEY
                }),
            },
            "optional": {
                "timeout": ("INT", {
                    "default": DEFAULT_TIMEOUT,
                    "min": 60,
                    "max": 1800
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "transform"
    CATEGORY = "RunningHub"

    def transform(self, image, prompt, webapp_id, api_key, timeout=DEFAULT_TIMEOUT):
        """Transform image with prompt"""

        if not webapp_id or not api_key:
            raise ValueError("RunningHub credentials are required")

        api = RunningHubAPI(webapp_id, api_key)

        # Convert tensor to PIL Image and save temporarily
        i = 255. * image.cpu().numpy()[0]
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Save to temp file
        temp_dir = folder_paths.get_temp_directory()
        temp_filename = f"runninghub_upload_{hashlib.md5(str(os.urandom(32)).encode()).hexdigest()}.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        img.save(temp_path)

        try:
            # Upload image
            print("Uploading image to RunningHub...")
            file_id = api.upload_image(temp_path)
            print(f"Image uploaded: {file_id}")

            # Prepare node info
            node_info = [
                {
                    "fieldName": "image",
                    "fieldValue": file_id,
                    "description": "Source image"
                },
                {
                    "fieldName": "prompt",
                    "fieldValue": prompt,
                    "description": "Transformation prompt"
                }
            ]

            print(f"Submitting image-to-image task with prompt: {prompt[:50]}...")

            # Submit task
            task_id = api.submit_task(NODE_IDS["image_to_image"], node_info)
            print(f"Task submitted: {task_id}")

            # Wait for result
            result_urls = api.wait_for_task(task_id, timeout=timeout)

            if not result_urls:
                raise Exception("No images generated")

            # Download and convert first image to ComfyUI format
            image_url = result_urls[0]
            print(f"Downloading image from: {image_url}")

            response = requests.get(image_url)
            response.raise_for_status()

            output_image = Image.open(BytesIO(response.content))
            output_image = output_image.convert("RGB")

            # Convert to tensor format
            image_np = np.array(output_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            return (image_tensor,)

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class RunningHubImageEnhancer:
    """Enhance image quality using RunningHub API"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "webapp_id": ("STRING", {
                    "default": RUNNINGHUB_WEBAPP_ID
                }),
                "api_key": ("STRING", {
                    "default": RUNNINGHUB_API_KEY
                }),
            },
            "optional": {
                "timeout": ("INT", {
                    "default": DEFAULT_TIMEOUT,
                    "min": 60,
                    "max": 1800
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "enhance"
    CATEGORY = "RunningHub"

    def enhance(self, image, webapp_id, api_key, timeout=DEFAULT_TIMEOUT):
        """Enhance image quality"""

        if not webapp_id or not api_key:
            raise ValueError("RunningHub credentials are required")

        api = RunningHubAPI(webapp_id, api_key)

        # Convert tensor to PIL Image and save temporarily
        i = 255. * image.cpu().numpy()[0]
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Save to temp file
        temp_dir = folder_paths.get_temp_directory()
        temp_filename = f"runninghub_upload_{hashlib.md5(str(os.urandom(32)).encode()).hexdigest()}.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        img.save(temp_path)

        try:
            # Upload image
            print("Uploading image to RunningHub...")
            file_id = api.upload_image(temp_path)
            print(f"Image uploaded: {file_id}")

            # Prepare node info
            node_info = [
                {
                    "fieldName": "image",
                    "fieldValue": file_id,
                    "description": "Image to enhance"
                }
            ]

            print("Submitting image enhancement task...")

            # Submit task
            task_id = api.submit_task(NODE_IDS["image_enhancer"], node_info)
            print(f"Task submitted: {task_id}")

            # Wait for result
            result_urls = api.wait_for_task(task_id, timeout=timeout)

            if not result_urls:
                raise Exception("No images generated")

            # Download and convert first image to ComfyUI format
            image_url = result_urls[0]
            print(f"Downloading image from: {image_url}")

            response = requests.get(image_url)
            response.raise_for_status()

            output_image = Image.open(BytesIO(response.content))
            output_image = output_image.convert("RGB")

            # Convert to tensor format
            image_np = np.array(output_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]

            return (image_tensor,)

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class RunningHubImageToVideo:
    """Convert images to videos using RunningHub API"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "webapp_id": ("STRING", {
                    "default": RUNNINGHUB_WEBAPP_ID
                }),
                "api_key": ("STRING", {
                    "default": RUNNINGHUB_API_KEY
                }),
            },
            "optional": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "timeout": ("INT", {
                    "default": DEFAULT_TIMEOUT,
                    "min": 60,
                    "max": 1800
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "convert"
    CATEGORY = "RunningHub"

    def convert(self, image, webapp_id, api_key, prompt="", timeout=DEFAULT_TIMEOUT):
        """Convert image to video"""

        if not webapp_id or not api_key:
            raise ValueError("RunningHub credentials are required")

        api = RunningHubAPI(webapp_id, api_key)

        # Convert tensor to PIL Image and save temporarily
        i = 255. * image.cpu().numpy()[0]
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Save to temp file
        temp_dir = folder_paths.get_temp_directory()
        temp_filename = f"runninghub_upload_{hashlib.md5(str(os.urandom(32)).encode()).hexdigest()}.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        img.save(temp_path)

        try:
            # Upload image
            print("Uploading image to RunningHub...")
            file_id = api.upload_image(temp_path)
            print(f"Image uploaded: {file_id}")

            # Prepare node info
            node_info = [
                {
                    "fieldName": "image",
                    "fieldValue": file_id,
                    "description": "Source image"
                }
            ]

            if prompt:
                node_info.append({
                    "fieldName": "prompt",
                    "fieldValue": prompt,
                    "description": "Video generation prompt"
                })

            print("Submitting image-to-video task...")

            # Submit task
            task_id = api.submit_task(NODE_IDS["image_to_video"], node_info)
            print(f"Task submitted: {task_id}")

            # Wait for result
            result_urls = api.wait_for_task(task_id, timeout=timeout)

            if not result_urls:
                raise Exception("No video generated")

            video_url = result_urls[0]
            print(f"Video generated: {video_url}")

            return (video_url,)

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class RunningHubLoadImage:
    """Load an image from URL"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "load"
    CATEGORY = "RunningHub"

    def load(self, url):
        """Load image from URL"""

        print(f"Loading image from: {url}")

        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")

        # Convert to tensor format
        image_np = np.array(image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        return (image_tensor,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "RunningHubTextToImage": RunningHubTextToImage,
    "RunningHubImageToImage": RunningHubImageToImage,
    "RunningHubImageEnhancer": RunningHubImageEnhancer,
    "RunningHubImageToVideo": RunningHubImageToVideo,
    "RunningHubLoadImage": RunningHubLoadImage,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "RunningHubTextToImage": "RunningHub Text to Image",
    "RunningHubImageToImage": "RunningHub Image to Image",
    "RunningHubImageEnhancer": "RunningHub Image Enhancer",
    "RunningHubImageToVideo": "RunningHub Image to Video",
    "RunningHubLoadImage": "RunningHub Load Image",
}
