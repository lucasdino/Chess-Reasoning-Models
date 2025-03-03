import re


# ====================================================
# Defining a couple custom exceptions
# ====================================================
class TimeoutError(Exception):
    """Exception raised when the chat request times out."""
    def __init__(self, message="The request timed out."):
        super().__init__(message)

class GenerationError(Exception):
    """Exception raised when the generation fails."""
    def __init__(self, message="The generation failed."):
        super().__init__(message)

class ExtractionError(Exception):
    """Exception raised when we're unable to properly extract the answer from the model."""
    def __init__(self, message="Model generation not formatted properly -- unable to extract answer."):
        super().__init__(message)

class IllegalMoveError(Exception):
    """Exception raised when the model generates an illegal move."""
    def __init__(self, message="The model generated an illegal move."):
        super().__init__(message)

# ====================================================
# Defining a couple custom exceptions
# ====================================================
def extract_answer(text: str) -> str:
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
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if not match:
        raise ExtractionError("No <answer> tags found.")
    
    # Strip leading/trailing whitespace and quotes
    extracted = match.group(1).strip()
    extracted = re.sub(r'^["\']|["\']$', '', extracted)  # Remove single/double quotes at edges

    # Ensure it only contains alphanumeric characters
    if not re.fullmatch(r"[A-Za-z0-9 ]+", extracted):
        raise ExtractionError("Extracted text contains invalid characters.")

    return extracted