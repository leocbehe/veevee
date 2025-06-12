# app/llm.py
import sys
from typing import Optional, Iterator
from .config import settings

from huggingface_hub import InferenceClient
from ollama import Client as OllamaClient
from ollama import ChatResponse
from collections.abc import Iterator


class LLMService:

    # Load environment variables from .env file

    def __init__(self, 
                 model_name: str, 
                 inference_provider: Optional[str] = None,
                 inference_url: Optional[str] = None,
                 token: Optional[str] = None, 
                 stream: bool = True,
                 temperature: float = 0.7,
                 max_response_tokens: int = 2000,
                 system_context_allowed: bool = False,
                 top_p: float = 0.9):
        self.inference_provider = inference_provider
        self.token = token if token else settings.hf_token
        self.inference_url = inference_url
        self.stream = stream
        self.temperature = temperature
        self.max_response_tokens = max_response_tokens
        self.system_context_allowed = system_context_allowed
        self.top_p = top_p
        if inference_provider == "ollama":
            self.model_name = model_name if model_name else settings.default_ollama_model
            self.client = OllamaClient(host=inference_url)
        elif inference_provider == "huggingface":
            # default case is to use huggingface inference.
            self.model_name = model_name if model_name else settings.default_hf_model
            self.client = InferenceClient(model=self.model_name, token=self.token, timeout=60)
        else:
            raise ValueError("Invalid inference provider")

    def generate(self, prompt):
        """
        Generates a response from the LLM based on the given prompt.

        Args:
            prompt (List[Dict]): The prompt to send to the LLM. If no chat history is provided, this should be a list of length one, with 
            the current user input message as the first element.
            max_response_tokens (int): The maximum length of the generated response.
            temperature (float): The temperature to use for sampling.
            top_p (float): The top_p value to use for sampling.

        Returns:
            ChatCompletionOutput: The generated response from the LLM.
        """
        if type(self.client) == OllamaClient:
            try:
                # this is temporary until i find a better workaround- otherwise, pylance will complain that self.client might be InferenceClient, which doesn't have a chat method,
                # and vice versa for OllamaClient.
                response = self.client.chat(
                    model=self.model_name,
                    messages=prompt, 
                    stream=self.stream,
                    options={
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "num_predict": self.max_response_tokens,
                    }
                )
                return response
            except Exception as e:
                print(f"Error generating response from ollama: {e}")
                return None
        elif type(self.client) == InferenceClient:
            try:
                response = self.client.chat_completion(
                    messages=prompt,
                    max_tokens=self.max_response_tokens,
                    temperature=self.temperature,
                    stream=self.stream,
                    top_p=self.top_p
                )
                return response
            except Exception as e:
                print(f"Error generating response from huggingface: {e}")
                return None