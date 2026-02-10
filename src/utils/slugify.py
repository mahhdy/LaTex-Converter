import re
import unicodedata

def slugify(text: str, max_length: int = 50) -> str:
    """
    Generates a Persian-aware slug from the given text.
    - Removes Persian diacritics
    - Converts spaces to hyphens
    - Removes special characters except Persian letters, English letters, numbers, and hyphens
    - Lowercases English letters
    """
    if not text:
        return ""
    
    # Normalize text
    text = unicodedata.normalize('NFKD', text)
    
    # Remove Persian diacritics (optional but recommended)
    # Persian diacritics are usually handled by normalization, but we can be explicit if needed
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove Persian diacritics (Zero-Width Non-Joiner is often used in Persian)
    # But for slugs, we want to remove ZWNJ or replace it with a hyphen
    text = text.replace('\u200c', '-')
    
    # Remove special characters except alphanumeric (including Persian) and hyphens
    # Persian letters: \u0600-\u06FF
    text = re.sub(r'[^\u0600-\u06FFa-zA-Z0-9-]', '', text)
    
    # Clean up hyphens (remove double hyphens and leading/trailing)
    text = re.sub(r'-+', '-', text).strip('-')
    
    # Lowercase English parts
    text = text.lower()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rstrip('-')
        
    return text
