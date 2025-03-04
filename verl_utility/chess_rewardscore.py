# Python file to extract answer from model output and compute reward score
# Direction from this file: https://github.com/volcengine/verl/blob/main/verl/utils/reward_score/gsm8k.py
# Better explained by this: https://verl.readthedocs.io/en/latest/preparation/reward_function.html

# Drop this into the following folder: verl/utils/reward_score/

import re


def extract_solution(text: str) -> str:
    """
    Extracts text between <answer> and </answer> tags, trims it, and returns it.
    Raises ExtractionError if no such text exists.
    
    Args:
        text (str): The input string containing the <answer> tags.
    
    Returns:
        str: The trimmed extracted text.
    
    Raises:
        ExtractionError: If the <answer> tags are not found.
    """
    failure_response = None

    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if not match:
        # raise ExtractionError("No <answer> tags found.")
        return failure_response

    # Strip leading/trailing whitespace and quotes
    extracted = match.group(1).strip()
    extracted = re.sub(r'^["\']|["\']$', '', extracted)  # Remove single/double quotes at edges

    # Ensure it only contains alphanumeric characters
    if not re.fullmatch(r"[A-Za-z0-9 ]+", extracted):
        # raise ExtractionError("Extracted text contains invalid characters.")
        return failure_response
    
    return extracted


def compute_score(solution_str, ground_truth, method='strict', format_score=0.):
    """
    The scoring function for our chess engine's RL learning loop.
    
    Args:
        solution_str (str): The model's output string.
        ground_truth (str): The ground truth answer (dict of move to reward -- defined in our dataprocessing code)
    """
    answer = extract_solution(solution_str)
    if answer is None:
        # Extraction error -- not formatted properly
        return 0
    else:
        if answer in ground_truth:
            return ground_truth[answer] + format_score
        else:
            # Optionally give a small reward for at least giving us a valid looking move
            return format_score