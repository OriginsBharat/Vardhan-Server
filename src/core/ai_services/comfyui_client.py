import httpx
import websockets
import json
import uuid

class ComfyUIClient:
    """A client for generating images with a local ComfyUI server."""
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    async def _get_image(self, filename, subfolder, folder_type):
        """Fetches the generated image data from the server."""
        async with httpx.AsyncClient() as client:
            url = f"http://{self.server_address}/view"
            params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.content

    async def generate_art(self, positive_prompt, negative_prompt=""):
        """
        Generates art using a standard text-to-image workflow.

        Args:
            positive_prompt (str): The description of the image to generate.
            negative_prompt (str): The description of what to avoid in the image.

        Returns:
            bytes: The raw image data, or None if generation fails.
        """
        # A standard SDXL text-to-image workflow
        prompt_workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 15668, # Placeholder, should be randomized
                    "steps": 25,
                    "cfg": 7,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": { "ckpt_name": "sd_xl_base_1.0.safetensors" }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": { "text": positive_prompt, "clip": ["4", 1] }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": { "text": negative_prompt, "clip": ["4", 1] }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": { "samples": ["3", 0], "vae": ["4", 2] }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": { "filename_prefix": "MyAIWorld", "images": ["8", 0] }
            }
        }

        # Queue the prompt
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"http://{self.server_address}/prompt", json={"prompt": prompt_workflow, "client_id": self.client_id})
                response.raise_for_status()
                prompt_id = response.json()['prompt_id']

            # Wait for the result via WebSocket
            uri = f"ws://{self.server_address}/ws?clientId={self.client_id}"
            async with websockets.connect(uri) as websocket:
                while True:
                    out = await websocket.recv()
                    if isinstance(out, str):
                        message = json.loads(out)
                        if message['type'] == 'executed':
                            data = message['data']
                            if data['node'] == "9": # The SaveImage node
                                image_data = data['output']['images'][0]
                                return await self._get_image(image_data['filename'], image_data['subfolder'], image_data['type'])
        except Exception as e:
            print(f"[ERROR] ComfyUI image generation failed: {e}")
            return None