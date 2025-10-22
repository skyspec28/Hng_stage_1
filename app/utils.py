import hashlib
from collections import Counter
from .schemas import CharacterProperties, FiltersApplied


def analyze_string(value: str) -> CharacterProperties:
    """
    Analyze a string and compute its properties.
    """
    length = len(value)

    cleaned_str = ''.join(c.lower() for c in value if c.isalnum())
    is_palindrome = cleaned_str == cleaned_str[::-1]

    unique_characters = len(set(value))

    word_count = len(value.split())

    sha256_hash = hashlib.sha256(value.encode()).hexdigest()

    character_frequency_map = dict(Counter(value))

    return CharacterProperties(
        length=length,
        is_palindrome=is_palindrome,
        unique_characters=unique_characters,
        word_count=word_count,
        sha256_hash=sha256_hash,
        character_frequency_map=character_frequency_map
    )


def validate_filters(filters_applied: FiltersApplied):
    """
    Validate filter parameters
    """
    if filters_applied.min_length is not None:
        if not isinstance(filters_applied.min_length, int):
            raise ValueError("min_length must be an integer")
        if filters_applied.min_length < 0:
            raise ValueError("min_length must be non-negative")
    
    if filters_applied.max_length is not None:
        if not isinstance(filters_applied.max_length, int):
            raise ValueError("max_length must be an integer")
        if filters_applied.max_length < 0:
            raise ValueError("max_length must be non-negative")
    
    if (filters_applied.min_length is not None and 
        filters_applied.max_length is not None):
        if filters_applied.min_length > filters_applied.max_length:
            raise ValueError("min_length cannot be greater than max_length")
    
    if filters_applied.word_count is not None:
        if not isinstance(filters_applied.word_count, int):
            raise ValueError("word_count must be an integer")
        if filters_applied.word_count < 0:
            raise ValueError("word_count must be non-negative")
    
    if filters_applied.contains_character is not None:
        if not isinstance(filters_applied.contains_character, str):
            raise ValueError("contains_character must be a string")
        if len(filters_applied.contains_character) != 1:
            raise ValueError("contains_character must be a single character")
    
    if filters_applied.is_palindrome is not None:
        if not isinstance(filters_applied.is_palindrome, bool):
            raise ValueError("is_palindrome must be a boolean")


def parse_natural_language_query(query: str) -> FiltersApplied:
    """
    Parse natural language query into filters
    """
    if not query:
        raise ValueError("Query cannot be empty")
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    
    filters = FiltersApplied()
    query = query.lower().strip()
    
    if "palindrom" in query:
        filters.is_palindrome = True
    
    if "single word" in query or "one word" in query:
        filters.word_count = 1
    elif "two words" in query:
        filters.word_count = 2
    elif "three words" in query:
        filters.word_count = 3
    
    if "longer than" in query or "more than" in query:
        try:
            words = query.split()
            idx = words.index("than")
            length = int(words[idx + 1])
            filters.min_length = length + 1
        except (ValueError, IndexError):
            pass
            
    if "shorter than" in query or "less than" in query:
        try:
            words = query.split()
            idx = words.index("than")
            length = int(words[idx + 1])
            filters.max_length = length - 1
        except (ValueError, IndexError):
            pass
    
    for phrase in ["containing", "contains", "with", "has"]:
        if phrase + " the letter " in query:
            try:
                char = query.split(phrase + " the letter ")[1][0]
                filters.contains_character = char
            except IndexError:
                continue
    
    if not any([
        filters.is_palindrome,
        filters.min_length,
        filters.max_length,
        filters.word_count,
        filters.contains_character
    ]):
        raise ValueError("Could not extract any valid filters from the query")
    
    validate_filters(filters)
    
    return filters