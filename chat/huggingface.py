import os
import torch
import multiprocessing
from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer

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
def _call_huggingface_chat(model_name, messages, use_cuda, output_queue):
    try:
        print("CALLING HUGGING FACE")
        device = "cuda" if use_cuda and torch.cuda.is_available() else "cpu"
        print(model_name, device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(tokenizer.chat_template)
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        print("MODEL CREATED")
        # Construct the conversation history
        chat_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        input_ids = tokenizer.encode(chat_text, return_tensors="pt").to(device)
        print("CHAT")
        print(chat_text)

        # Explicitly set attention mask
        attention_mask = torch.ones_like(input_ids).to(device)

        # Ensure `pad_token_id` is correctly set
        pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id

        with torch.no_grad():
            output_ids = model.generate(
                input_ids, 
                attention_mask=attention_mask,  # Avoids the warning
                max_length=4000, 
                do_sample=True,
                pad_token_id=pad_token_id  # Ensures reliable behavior
            )
        
        print("OUTPUT GENERATED")
        print(output_ids)
        response_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        print(response_text)
        # Store some runtime statistics (timings are approximations)
        runtime_results = {
            "prompt_tokens": input_ids.shape[1], 
            "generated_tokens": output_ids.shape[1] - input_ids.shape[1], 
            "completion_reason": "length" if output_ids.shape[1] >= 4000 else "finished",
        }
        print("ADDED TO QUEUE")
        output_queue.put((response_text, runtime_results))
    except Exception as e:
        output_queue.put({"error": str(e)})

class HuggingFaceSession:
    def __init__(self, model_name="DeepSeek-R1-Distill-Qwen-1.5B", use_cuda=True, board_representation="FEN"):
        """
        Initializes the HuggingFaceSession with a model and board representation.

        Args:
            model_name (str): The name of the Hugging Face model to use.
            use_cuda (bool): Whether to use CUDA for acceleration.
            board_representation (str): The type of board representation (e.g., "FEN", "desc").
        """
        self.model_name = model_name
        self.use_cuda = use_cuda
        self.board_representation = board_representation
        self.cached_messages = _get_cached_system_messages(board_representation)
    
    def chat(self, user_prompt, timeout=15):
        messages = self.cached_messages + [{"role": "user", "content": user_prompt}]
        output_queue = multiprocessing.Queue()

        process = multiprocessing.Process(
            target=_call_huggingface_chat,
            args=(self.model_name, messages, self.use_cuda, output_queue)
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            raise TimeoutError(f"The chat request exceeded the timeout limit ({timeout} seconds).")

        if not output_queue.empty():
            response = output_queue.get()
            if isinstance(response, dict) and "error" in response:
                raise GenerationError(response["error"])
            return response  # (response_text, runtime_results)
        else:
            raise GenerationError("The generation failed.")
