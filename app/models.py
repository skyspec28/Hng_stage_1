from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func


class StringAnalysis(Base):
    __tablename__ = "string_analysis"

    id = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True)
    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False)
    character_frequency_map = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())