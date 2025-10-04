# src/core/ai_services/comfyui_client.py
# Client for interacting with a self-hosted ComfyUI instance for art generation.

import websocket
import uuid
import json
import urllib.request
import urllib.parse
import logging
import random
from typing import Optional

from src.config import Config

class ComfyUIClient:
    """
    Interfaces with a ComfyUI server to generate images from text prompts.
    """
    def __init__(self, config: Config):
        self.config = config
        self.server_address = self.config.COMFYUI_API_URL
        # Extract hostname and port for websocket
        ws_address = self.server_address.replace('http://', '').replace('https://', '')
        self.ws_address = ws_address
        self.client_id = str(uuid.uuid4())
        logging.info("ComfyUIClient initialized.")

    def _get_image(self, filename: str, subfolder: str, folder_type: str) -> Optional[bytes]:
        """Fetches the generated image data from the ComfyUI server."""
        try:
            data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            url_values = urllib.parse.urlencode(data)
            with urllib.request.urlopen(f"{self.server_address}/view?{url_values}") as response:
                return response.read()
        except Exception as e:
            logging.error(f"Failed to fetch image from ComfyUI server: {e}")
            return None

    def _queue_prompt(self, prompt_workflow: dict) -> Optional[str]:
        """Sends a prompt workflow to the ComfyUI queue."""
        try:
            p = {"prompt": prompt_workflow, "client_id": self.client_id}
            data = json.dumps(p).encode('utf-8')
            req = urllib.request.Request(f"{self.server_address}/prompt", data=data)
            response = json.loads(urllib.request.urlopen(req).read())
            return response.get('prompt_id')
        except Exception as e:
            logging.error(f"Failed to queue prompt with ComfyUI: {e}")
            return None

    def _get_history(self, prompt_id: str) -> dict:
        """Gets the execution history for a given prompt ID."""
        try:
            with urllib.request.urlopen(f"{self.server_address}/history/{prompt_id}") as response:
                return json.loads(response.read())
        except Exception as e:
            logging.error(f"Failed to get history from ComfyUI: {e}")
            return {}

    async def generate_art(self, positive_prompt: str, negative_prompt: str = "bad quality, worst quality, lowres") -> Optional[str]:
        """
        Generates an image using a standard text-to-image workflow.

        Args:
            positive_prompt: The description of the image to create.
            negative_prompt: Concepts to avoid in the image.

        Returns:
            The file path of the saved image if successful, otherwise None.
        """
        # This is a standard, simple text-to-image workflow for SDXL 1.0.
        # It can be expanded or customized in the future.
        prompt_workflow = {
            "3": {"class_type": "KSampler", "inputs": {"seed": random.randint(1, 2**64), "steps": 25, "cfg": 8.0, "sampler_name": "dpmpp_2m_sde_gpu", "scheduler": "karras", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive_prompt, "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "MyAIWorld", "images": ["8", 0]}}
        }

        logging.info(f"Queueing ComfyUI art generation prompt: '{positive_prompt[:70]}...'")

        ws = None
        try:
            prompt_id = self._queue_prompt(prompt_workflow)
            if not prompt_id:
                return None

            ws = websocket.WebSocket()
            ws.connect(f"ws://{self.ws_address}/ws?clientId={self.client_id}")

            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing' and message['data']['prompt_id'] == prompt_id:
                        if message['data']['node'] is None: # Execution is complete
                            break

            history = self._get_history(prompt_id).get(prompt_id, {})
            if not history:
                logging.error("Failed to retrieve execution history from ComfyUI.")
                return None

            # Find the output from the SaveImage node (ID '9')
            output_data = history.get('outputs', {}).get('9', {})
            images = output_data.get('images', [])
            if not images:
                logging.error("No images found in the output from ComfyUI.")
                return None

            image_info = images[0]
            image_data = self._get_image(image_info['filename'], image_info['subfolder'], image_info['type'])

            if not image_data:
                return None

            output_path = f"art_gallery/{image_info['filename']}"
            with open(output_path, "wb") as f:
                f.write(image_data)

            logging.info(f"Successfully generated and saved art to {output_path}")
            return output_path

        except Exception as e:
            logging.error(f"An unexpected error occurred during ComfyUI communication. Is the server running? Error: {e}")
            return None
        finally:
            if ws and ws.connected:
                ws.close()