import re

def enforce_action_text_format(text: str) -> str:
    """
    Ensures the output text strictly follows the '*action* text *action*' format.
    This is a simple implementation; a more complex one could use NLP to better distinguish
    dialogue from actions if the LLM fails to format it correctly.
    """
    # 1. Strip leading/trailing whitespace and remove any errant quotation marks at the ends
    text = text.strip().strip('"')

    # 2. Check if the text already seems to be in the correct format.
    if text.startswith('*') and text.endswith('*'):
        # Split by the asterisks. A valid format would be ['', 'action', ' text ', 'action', '']
        parts = text.split('*')
        # Check if there's content between the asterisks
        if len(parts) > 2 and any(p.strip() for p in parts[1:-1]):
            return text  # Assume it's already well-formatted

    # 3. If not, assume the entire text is dialogue and wrap it.
    # This is a fallback for when the LLM forgets the format.
    return f"*{text}*"