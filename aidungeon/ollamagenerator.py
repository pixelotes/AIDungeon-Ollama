# aidungeon/ollamagenerator.py
import requests
import json
import re
from typing import Union, Optional, List
from pathlib import Path
from .getconfig import settings, logger, get_ollama_model, get_ollama_host
from .utils import cut_trailing_sentence, output, clear_lines, format_result, use_ptoolkit

class OllamaGenerator:
    """
    Ollama-based text generator to replace GPT2Generator.
    This separates the game logic from model management by delegating to Ollama.
    """
    
    def __init__(
            self, 
            model_name: str = "llama2:7b",
            ollama_host: str = "http://localhost:11434",
            generate_num: int = 60,
            temperature: float = 0.4,
            top_k: int = 40,
            top_p: float = 0.9,
            repetition_penalty: float = 1.0,
            repetition_penalty_range: int = 512,
            repetition_penalty_slope: float = 3.33
    ):
        """
        Initialize the Ollama generator.
        """
        self.model_name = model_name
        self.ollama_host = ollama_host.rstrip('/')
        self.generate_num = generate_num
        self.temp = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty
        self.repetition_penalty_range = repetition_penalty_range
        self.repetition_penalty_slope = repetition_penalty_slope
        
        self._validate_setup()
        
        self.max_history_tokens = self._get_context_length() - generate_num
        
        logger.info(f"Initialized OllamaGenerator with model: {model_name}")
        logger.info(f"Max token history: {self.max_history_tokens}")
    
    def _validate_setup(self):
        """Validate Ollama connection and model availability."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            available_models = [model['name'] for model in models]
            
            if self.model_name not in available_models:
                logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
                if available_models:
                    logger.info("Consider pulling the model with: ollama pull " + self.model_name)
                else:
                    logger.warning("No models found. Make sure Ollama is running and has models installed.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Ollama at {self.ollama_host}: {e}")
            raise ConnectionError(f"Cannot connect to Ollama server at {self.ollama_host}")
    
    def _get_context_length(self) -> int:
        """Get the context length for the current model."""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/show",
                json={"name": self.model_name},
                timeout=10
            )
            response.raise_for_status()
            model_info = response.json()
            
            context_length = model_info.get('modelfile', '').find('num_ctx')
            if context_length == -1:
                if 'llama2' in self.model_name.lower():
                    return 4096
                elif 'mistral' in self.model_name.lower():
                    return 8192
                elif 'codellama' in self.model_name.lower():
                    return 16384
                else:
                    return 2048
            
            return 4096
            
        except requests.exceptions.RequestException:
            logger.warning("Could not determine model context length, using default")
            return 2048
    
    def _build_prompt(self, context: str, memory: List[str], story: str, action: str) -> str:
        """
        Build the complete prompt for the model.
        """
        memory_text = ' '.join(memory) if memory else ''
        full_context = f"{context} {memory_text}".strip()
        
        if story.strip():
            prompt = f"{full_context}\n\n{story}\n{action}"
        else:
            prompt = f"{full_context}\n{action}"
        
        max_chars = self.max_history_tokens * 4
        if len(prompt) > max_chars:
            context_len = len(full_context)
            if context_len < max_chars // 2:
                available_for_story = max_chars - context_len - len(action) - 10
                if available_for_story > 0:
                    story_truncated = story[-available_for_story:].strip()
                    sentences = story_truncated.split('. ')
                    if len(sentences) > 1:
                        story_truncated = '. '.join(sentences[1:])
                    prompt = f"{full_context}\n\n{story_truncated}\n{action}"
                else:
                    prompt = f"{full_context}\n{action}"
            else:
                context_truncated = full_context[-max_chars//2:].strip()
                prompt = f"{context_truncated}\n{action}"
        
        return prompt
    
    def _call_ollama(self, prompt: str, temperature: float, top_k: int, top_p: float, 
                    repetition_penalty: float, stop_tokens: Optional[List[str]] = None,
                    num_predict: Optional[int] = None) -> str:
        """Make a generation request to Ollama."""
        
        # Use the provided num_predict, or fall back to the class default
        final_num_predict = num_predict if num_predict is not None else self.generate_num

        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "repeat_penalty": repetition_penalty,
                "num_predict": final_num_predict,
            }
        }
        
        if stop_tokens:
            request_data["options"]["stop"] = stop_tokens
        
        try:
            if use_ptoolkit():
                clines = output("Generating...", "loading-message")
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=request_data,
                timeout=120
            )
            response.raise_for_status()
            
            if use_ptoolkit():
                clear_lines(clines)
            
            result = response.json()
            generated_text = result.get('response', '')
            
            logger.debug(f"Generated text: {repr(generated_text)}")
            return generated_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response: {e}")
            return ""
    
    def generate_raw(
            self, 
            context: str, 
            prompt: str = '', 
            generate_num: Optional[int] = None, 
            temperature: Optional[float] = None, 
            top_k: Optional[int] = None, 
            top_p: Optional[float] = None,
            repetition_penalty: Optional[float] = None, 
            repetition_penalty_range: Optional[int] = None, 
            repetition_penalty_slope: Optional[float] = None, 
            stop_tokens: Optional[List[str]] = None
    ) -> str:
        """
        Generate raw text using Ollama.
        """
        temperature = temperature if temperature is not None else self.temp
        top_k = top_k if top_k is not None else self.top_k
        top_p = top_p if top_p is not None else self.top_p
        repetition_penalty = repetition_penalty if repetition_penalty is not None else self.repetition_penalty
        
        full_prompt = f"{prompt}\n{context}".strip()
        
        logger.debug(f"Sending prompt to Ollama: {repr(full_prompt[:200])}")
        
        # Pass the generate_num override to the call function
        generated_text = self._call_ollama(
            full_prompt, temperature, top_k, top_p, repetition_penalty, stop_tokens,
            num_predict=generate_num
        )
        
        return generated_text
    
    def generate(
            self, 
            context: str, 
            prompt: str = '', 
            temperature: Optional[float] = None, 
            top_p: Optional[float] = None, 
            top_k: Optional[int] = None, 
            repetition_penalty: Optional[float] = None, 
            repetition_penalty_range: Optional[int] = None, 
            repetition_penalty_slope: Optional[float] = None, 
            depth: int = 0
    ) -> str:
        """
        Generate and format text for story continuation.
        """
        temperature = temperature if temperature is not None else self.temp
        top_k = top_k if top_k is not None else self.top_k
        top_p = top_p if top_p is not None else self.top_p
        repetition_penalty = repetition_penalty if repetition_penalty is not None else self.repetition_penalty
        
        logger.debug(f"Generating with temp={temperature}, top_k={top_k}, top_p={top_p}, rep_pen={repetition_penalty}")
        
        text = self.generate_raw(
            context, 
            prompt, 
            temperature=temperature, 
            top_k=top_k, 
            top_p=top_p, 
            repetition_penalty=repetition_penalty,
            stop_tokens=["<|endoftext|>", ">"]
        )
        
        logger.debug(f"Raw generated result: {repr(text)}")
        
        result = self.result_replace(text)
        
        if len(result) == 0 and depth < 6:
            result = self.result_replace(text, allow_action=True)
            logger.info(f"Empty generation, trying with allow_action=True: {repr(result)}")
        
        if len(result) == 0 and depth < 20:
            logger.info(f"Empty generation, retrying (depth={depth})")
            return self.generate(
                context, prompt, temperature=temperature, top_p=top_p, top_k=top_k,
                repetition_penalty=repetition_penalty, depth=depth + 1
            )
        elif len(result) == 0:
            logger.warning(f"Model generated empty text {depth} times. Consider trying different parameters.")
        
        return result
    
    def result_replace(self, result: str, allow_action: bool = False) -> str:
        """
        Post-process generated text.
        """
        result = cut_trailing_sentence(result, allow_action=allow_action)

        if len(result) == 0:
            return ""
        
        first_letter_capitalized = result[0].isupper()
        result = result.replace('."', '".')
        result = result.replace("#", "")
        result = result.replace("*", "")
        result = result.replace("\n\n", "\n")
        
        if not first_letter_capitalized:
            result = result[0].lower() + result[1:]

        return result


def get_generator():
    """
    Factory function to create an Ollama generator.
    """
    output("\nInitializing Ollama AI Engine!", "loading-message", end="\n\n")
    
    ollama_host = get_ollama_host()
    model_name = None
    
    try:
        response = requests.get(f"{ollama_host}/api/tags", timeout=10)
        response.raise_for_status()
        models_data = response.json()
        available_models = [model['name'] for model in models_data.get('models', [])]
        
        if not available_models:
            output("No models found in Ollama. Please pull a model first:", "error")
            output("Example: ollama pull llama2", "message")
            output("Then restart this application.", "message")
            exit(1)
        
    except requests.exceptions.RequestException:
        output("Cannot connect to Ollama. Make sure it's running at " + ollama_host, "error")
        output("Start Ollama with: ollama serve", "message")
        exit(1)

    configured_model = get_ollama_model()
    if configured_model in available_models:
        logger.info(f"Using configured model: {configured_model}")
        model_name = configured_model
    else:
        logger.warning(f"Configured model '{configured_model}' not found. Showing selection menu.")
        if len(available_models) == 1:
            model_name = available_models[0]
            logger.info(f"Using only available model: {model_name}")
        else:
            output("Available Ollama models:", "message")
            for i, model in enumerate(available_models):
                output(f"{i}) {model}", "menu")
            output(f"{len(available_models)}) Exit", "menu")
            
            while True:
                try:
                    selection = input("Select a model: ").strip()
                    if not selection:
                        selection = "0"
                    selection = int(selection)
                    
                    if selection == len(available_models):
                        output("Exiting.", "message")
                        exit(0)
                    elif 0 <= selection < len(available_models):
                        model_name = available_models[selection]
                        break
                    else:
                        output("Invalid selection.", "error")
                except ValueError:
                    output("Please enter a number.", "error")
    
    try:
        generator = OllamaGenerator(
            model_name=model_name,
            ollama_host=ollama_host,
            generate_num=settings.getint("generate-num"),
            temperature=settings.getfloat("temp"),
            top_k=settings.getint("top-keks"),
            top_p=settings.getfloat("top-p"),
            repetition_penalty=settings.getfloat("rep-pen"),
            repetition_penalty_range=settings.getint("rep-pen-range"),
            repetition_penalty_slope=settings.getfloat("rep-pen-slope"),
        )
        return generator
        
    except Exception as e:
        output(f"Failed to initialize Ollama generator: {e}", "error")
        exit(1)


def memory_merge(prompt: str, context: str, max_length: int = 2000) -> str:
    """
    Simple text-based context merging.
    """
    combined = f"{prompt}\n{context}".strip()
    
    if len(combined) > max_length:
        if len(prompt) < max_length // 2:
            available = max_length - len(prompt) - 10
            context_truncated = context[-available:] if available > 0 else ""
            words = context_truncated.split()
            if len(words) > 1:
                context_truncated = ' '.join(words[1:])
            combined = f"{prompt}\n{context_truncated}".strip()
        else:
            combined = prompt[-max_length:].strip()
    
    return combined