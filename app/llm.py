# app/llm.py
import sys
from typing import Optional
from .config import settings

from huggingface_hub import InferenceClient, ChatCompletionOutput
from ollama import Client as OllamaClient


class LLMService:

    # Load environment variables from .env file

    def __init__(self, model_name: str = None, token: Optional[str] = None, inference_provider: str = settings.inference_provider, inference_url: Optional[str] = "http://127.0.0.1:11434"):
        self.inference_provider = inference_provider if inference_provider else "huggingface"
        self.token = token if token else settings.hf_token
        if not token:
            print("""WARNING: no token provided. This may cause an error when attempting to 
                  run inference from a remote or third-party provider.""", file=sys.stderr)
        if inference_provider == "ollama":
            self.model_name = model_name if model_name else settings.default_ollama_model
            self.client = OllamaClient(host=inference_url)
        else:
            # default case is to use huggingface inference.
            self.model_name = model_name if model_name else settings.default_hf_model
            self.client = InferenceClient(provider=inference_provider, model=self.model_name, token=self.token)

    def generate(self, prompt, max_length: int = 800, temperature: float = 0.7, top_p: float = 0.9) -> str:
        """
        Generates a response from the LLM based on the given prompt.

        Args:
            prompt (List[Dict]): The prompt to send to the LLM. If no chat history is provided, this should be a list of length one, with 
            the current user input message as the first element.
            max_length (int): The maximum length of the generated response.
            temperature (float): The temperature to use for sampling.
            top_p (float): The top_p value to use for sampling.

        Returns:
            ChatCompletionOutput: The generated response from the LLM.
        """
        if self.inference_provider == "ollama":
            try:
                response = self.client.chat(
                    model=self.model_name,
                    messages=prompt, 
                    options={
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_length,
                    }
                )
                print(f"Response class: {type(response)}")
                print(f"Response: {response}")
                return response
            except Exception as e:
                print(f"Error generating response: {e}")
                return None
        else:
            try:
                response = self.client.chat_completion(
                    messages=prompt,
                    max_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p
                )   
                return response
            except Exception as e:
                print(f"Error generating response: {e}")
                return None