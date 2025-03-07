import os
import ollama
import multiprocessing
from functools import lru_cache

from .utility import TimeoutError, GenerationError


# Cache the system prompt once.
@lru_cache(maxsize=1)
def _get_cached_system_messages(board_representation):
    """
    Loads and caches the system prompt based on board representation.
    """
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f'{cur_dir}/systemprompt_{board_representation}.txt', 'r') as file:
        system_prompt = file.read()
    return [{"role": "system", "content": system_prompt}]


# This function runs in a separate process.
def _call_ollama_chat(model, messages, options, output_queue):
    try:
        response = ollama.chat(model=model, messages=messages, options=options)
        output_queue.put(response)
    except Exception as e:
        output_queue.put({"error": str(e)})

class OllamaSession:
    def __init__(self, model="deepseek-r1:1.5b", use_cuda=True, board_representation="FEN"):
        """
        Initializes the OllamaSession with model and board representation.

        Args:
            model (str): The name of the model to use.
            use_cuda (bool): Whether to use CUDA for acceleration.
            board_representation (str): The type of board representation (e.g., "FEN", "desc").
        """
        self.model = model
        self.use_cuda = use_cuda
        self.board_representation = board_representation
        self.cached_messages = _get_cached_system_messages(board_representation)
    
    def chat(self, user_prompt, timeout=15):
        messages = self.cached_messages + [{"role": "user", "content": user_prompt}]
        options = {
            "num_gpu_layers": 10 if self.use_cuda else {},
            "max_tokens": 4000,
            "num_ctx": 5000
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
            raise TimeoutError(f"The chat request exceeded the timeout limit ({timeout} seconds).")
        if not output_queue.empty():
            response = output_queue.get()
            response_content = response["message"]["content"]
            # Store some runtime data and return it -- all time in seconds
            runtime_results = {
                "prompt_tokens": response["prompt_eval_count"], 
                "generated_tokens": response["eval_count"], 
                "completion_reason": response["done_reason"],
                "total_duration": response["total_duration"]/1e9,
                "prompt_eval_duration": response["prompt_eval_duration"]/1e9,
                "generation_duration": response["eval_duration"]/1e9,
            }
            return response_content, runtime_results
        else:
            raise GenerationError("The generation failed.")
