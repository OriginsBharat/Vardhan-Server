import httpx
import json
import logging
import time
import os
import uuid
from urllib.parse import urljoin
import asyncio

class ComfyUIClient:
    """
    Client for interacting with the ComfyUI API for image generation.
    """
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)

    async def generate_image(self, prompt: str, character_name: str) -> str:
        """
        Generates an image using a standard text-to-image workflow.

        Args:
            prompt: The text prompt describing the desired image.
            character_name: The name of the character generating the image, used for filenames.

        Returns:
            The file path of the generated image, or an error message.
        """
        self.logger.info(f"Generating image for prompt: {prompt}")

        # Standard, simple text-to-image workflow for SDXL
        workflow_prompt = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(time.time()),
                    "steps": 25,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "text, watermark, ugly, deformed, blurry",
                    "clip": ["4", 1]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": f"{character_name}_{uuid.uuid4()}",
                    "images": ["8", 0]
                }
            }
        }

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                post_url = urljoin(self.api_url, "/prompt")
                response = await client.post(post_url, json={"prompt": workflow_prompt})
                response.raise_for_status()
                prompt_id = response.json().get("prompt_id")
                if not prompt_id:
                    raise ValueError("Failed to get prompt ID from ComfyUI.")

                self.logger.info(f"Prompt queued with ID: {prompt_id}")

                while True:
                    history_url = urljoin(self.api_url, f"/history/{prompt_id}")
                    history_res = await client.get(history_url)
                    history_res.raise_for_status()
                    history_data = history_res.json()

                    if prompt_id in history_data and history_data[prompt_id].get("outputs"):
                        outputs = history_data[prompt_id]["outputs"]
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                image_data = node_output['images'][0]
                                filename = image_data['filename']

                                view_url = urljoin(self.api_url, f"/view?filename={filename}&subfolder={image_data.get('subfolder', '')}&type={image_data.get('type', 'output')}")

                                image_response = await client.get(view_url)
                                image_response.raise_for_status()

                                os.makedirs("art_gallery", exist_ok=True)
                                file_path = os.path.join("art_gallery", filename)
                                with open(file_path, "wb") as f:
                                    f.write(image_response.content)

                                self.logger.info(f"Image successfully generated and saved to {file_path}")
                                return file_path
                        break

                    await asyncio.sleep(2)

                raise ValueError("Image generation completed, but no image output was found.")

        except httpx.RequestError as e:
            self.logger.error(f"Error connecting to ComfyUI API: {e}")
            return f"Error: Could not connect to the ComfyUI server at {self.api_url}. Is it running?"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during image generation: {e}")
            return "Error: An unexpected error occurred while generating the image."