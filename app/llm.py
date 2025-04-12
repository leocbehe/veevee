# app/llm.py
import os
from typing import Optional
from .config import settings

from huggingface_hub import InferenceClient, TextGenerationOutput

class LLMService:

    # Load environment variables from .env file

    def __init__(self, model_name: str, token: Optional[str] = None):
        """
        Initializes the LLM service with a Hugging Face Inference Endpoint.

        Args:
            model_name (str): The name of the Hugging Face model to use.
            token (str, optional): Your Hugging Face API token. Defaults to None, which attempts to read from the environment.
        """
        self.model_name = model_name
        self.token = token if token else settings.hf_token
        if not self.token:
            raise ValueError("Hugging Face API token not found.  Set HUGGINGFACE_API_TOKEN environment variable or pass token directly.")
        self.client = InferenceClient(model=self.model_name, token=self.token)

    def generate(self, prompt, use_history: bool = False, max_length: int = 200, temperature: float = 0.7, top_p: float = 0.9) -> str:
        """
        Generates a response from the LLM based on the given prompt.

        Args:
            prompt (str): The prompt to send to the LLM.
            max_length (int): The maximum length of the generated response.
            temperature (float): The temperature to use for sampling.
            top_p (float): The top_p value to use for sampling.

        Returns:
            TextGenerationOutput: The generated response from the LLM.
        """
        response: TextGenerationOutput = None
        try:
            if use_history:
                response = self.client.chat_completion(
                    messages=prompt,
                    max_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p
                )
            else:
                response = self.client.text_generation(
                    prompt=prompt,
                    max_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    details=True
                )      
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return ""