# Example Workflows

This directory contains example ComfyUI workflow files for the RunningHub integration.

## Available Examples

### text_to_image_example.json

Basic text-to-image generation workflow:
- Uses `RunningHubTextToImage` node
- Generates an image from a text prompt
- Saves the output

**To use:**
1. Load this workflow in ComfyUI
2. Replace `your_webapp_id_here` and `your_api_key_here` with your actual credentials
3. Modify the prompt as desired
4. Queue the workflow

### image_enhancement_example.json

Image enhancement workflow:
- Loads an existing image
- Uses `RunningHubImageEnhancer` to enhance quality
- Saves the enhanced image

**To use:**
1. Load this workflow in ComfyUI
2. Replace `your_webapp_id_here` and `your_api_key_here` with your actual credentials
3. Select your source image in the LoadImage node
4. Queue the workflow

## Creating Your Own Workflows

You can combine these nodes with other ComfyUI nodes to create complex workflows. For example:

- Chain multiple transformations
- Use ControlNet with RunningHub generation
- Batch process multiple images
- Combine with upscalers and other enhancement tools

## Tips

- Make sure to set appropriate timeout values for longer operations
- The Image to Video node returns a URL - you'll need to manually download the video
- You can use the LoadImage node with URLs from previous generations
- All RunningHub nodes support the standard ComfyUI IMAGE format
