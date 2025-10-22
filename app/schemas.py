from pydantic import BaseModel, validator
from typing import Optional, Dict, List
from datetime import datetime


class CharacterProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class StringAnalysis(BaseModel):
    id: str
    value: str
    properties: CharacterProperties
    created_at: datetime

class StringCreate(BaseModel):
    value: str

    @validator('value')
    def validate_value(cls, v):
        if not v or not v.strip():
            raise ValueError("String value cannot be empty")
        return v.strip()

class StringResponse(StringAnalysis):
    pass

class FiltersApplied(BaseModel):
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    word_count: Optional[int] = None
    contains_character: Optional[str] = None

class StringList(BaseModel):
    data: List[StringAnalysis]
    count: int
    filters_applied: Optional[FiltersApplied] = None

class NaturalLanguageQuery(BaseModel):
    original: str
    parsed_filters: FiltersApplied

class NaturalLanguageResponse(BaseModel):
    data: List[StringAnalysis]
    count: int
    interpreted_query: NaturalLanguageQuery