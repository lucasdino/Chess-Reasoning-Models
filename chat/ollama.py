import os
import ollama
import multiprocessing
from functools import lru_cache

from .utility import TimeoutError, GenerationError


# Import our system prompt
cur_dir = os.path.dirname(os.path.abspath(__file__))
with open(f'{cur_dir}/systemprompt.txt', 'r') as file:
    SYSTEM_PROMPT = file.read()


# Cache the system prompt once.
@lru_cache(maxsize=1)
def _get_cached_system_messages():
    return [{"role": "system", "content": SYSTEM_PROMPT}]


# This function runs in a separate process.
def _call_ollama_chat(model, messages, options, output_queue):
    try:
        response = ollama.chat(model=model, messages=messages, options=options)
        output_queue.put(response)
    except Exception as e:
        output_queue.put({"error": str(e)})

class OllamaSession:
    def __init__(self, model="deepseek-r1:1.5b", use_cuda=True):
        self.model = model
        self.use_cuda = use_cuda
        self.cached_messages = _get_cached_system_messages()
    
    def chat(self, user_prompt, timeout=15):
        messages = self.cached_messages + [{"role": "user", "content": user_prompt}]
        options = {
            "num_gpu_layers": 10 if self.use_cuda else {},
            "max_tokens": 2500,
        }
        output_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_call_ollama_chat,
            args=(self.model, messages, options, output_queue)
        )
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            process.join()
            raise TimeoutError("The chat request exceeded the timeout limit.")
        if not output_queue.empty():
            response = output_queue.get()
            return response["message"]["content"]
        else:
            raise GenerationError("The generation failed.")