"""
ComfyUI RunningHub Integration
Custom nodes for using RunningHub API services in ComfyUI workflows
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Version info
__version__ = "1.0.0"
__author__ = "ComfyUI RunningHub"
__description__ = "RunningHub API integration for ComfyUI - Text to Image, Image to Image, Image Enhancement, and Image to Video"

# Display info when loading
print(f"[RunningHub] Loading RunningHub nodes v{__version__}")
print("[RunningHub] Available nodes:")
for node_name in NODE_DISPLAY_NAME_MAPPINGS.values():
    print(f"  - {node_name}")
