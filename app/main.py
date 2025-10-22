from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from . import models, schemas, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="String Analyzer API")

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.post("/strings", response_model=schemas.StringResponse, status_code=201)
def create_string(string: schemas.StringCreate, db: Session = Depends(get_db)):
    """
    Create and analyze a new string
    """
    properties = utils.analyze_string(string.value)
    
    db_string = models.StringAnalysis(
        id=properties.sha256_hash,
        value=string.value,
        length=properties.length,
        is_palindrome=properties.is_palindrome,
        unique_characters=properties.unique_characters,
        word_count=properties.word_count,
        sha256_hash=properties.sha256_hash,
        character_frequency_map=properties.character_frequency_map
    )
    
    try:
        db.add(db_string)
        db.commit()
        db.refresh(db_string)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="String already exists in the system"
        )
    
    db_dict = {c.name: getattr(db_string, c.name) for c in db_string.__table__.columns}
    
    return schemas.StringResponse(
        id=db_dict['id'],
        value=db_dict['value'],
        properties=properties,
        created_at=db_dict['created_at']
    )


@app.get("/strings/{string_value}", response_model=schemas.StringResponse)
def get_string(string_value: str, db: Session = Depends(get_db)):
    """
    Get a specific string by its value
    """
    db_string = db.query(models.StringAnalysis).filter(
        models.StringAnalysis.value == string_value
    ).first()
    
    if db_string is None:
        raise HTTPException(
            status_code=404,
            detail="String does not exist in the system"
        )
    
    db_dict = {c.name: getattr(db_string, c.name) for c in db_string.__table__.columns}
    
    properties = schemas.CharacterProperties(
        length=db_dict['length'],
        is_palindrome=db_dict['is_palindrome'],
        unique_characters=db_dict['unique_characters'],
        word_count=db_dict['word_count'],
        sha256_hash=db_dict['sha256_hash'],
        character_frequency_map=db_dict['character_frequency_map']
    )
    
    db_dict = {c.name: getattr(db_string, c.name) for c in db_string.__table__.columns}
    
    return schemas.StringResponse(
        id=db_dict['id'],
        value=db_dict['value'],
        properties=properties,
        created_at=db_dict['created_at']
    )


@app.get("/strings", response_model=schemas.StringList)
def list_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all strings with optional filters
    """
    filters = schemas.FiltersApplied(
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character
    )
    
    try:
        utils.validate_filters(filters)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    query = db.query(models.StringAnalysis)
    
    if is_palindrome is not None:
        query = query.filter(models.StringAnalysis.is_palindrome == is_palindrome)
    
    if min_length is not None:
        query = query.filter(models.StringAnalysis.length >= min_length)
    
    if max_length is not None:
        query = query.filter(models.StringAnalysis.length <= max_length)
    
    if word_count is not None:
        query = query.filter(models.StringAnalysis.word_count == word_count)
    
    if contains_character is not None:
        query = query.filter(
            models.StringAnalysis.value.contains(contains_character)  # type: ignore
        )
    
    strings = query.all()
    
    string_responses = []
    for db_string in strings:
        db_dict = {c.name: getattr(db_string, c.name) for c in db_string.__table__.columns}
        
        properties = schemas.CharacterProperties(
            length=db_dict['length'],
            is_palindrome=db_dict['is_palindrome'],
            unique_characters=db_dict['unique_characters'],
            word_count=db_dict['word_count'],
            sha256_hash=db_dict['sha256_hash'],
            character_frequency_map=db_dict['character_frequency_map']
        )
        
        string_responses.append(
            schemas.StringAnalysis(
                id=db_dict['id'],
                value=db_dict['value'],
                properties=properties,
                created_at=db_dict['created_at']
            )
        )
    
    return schemas.StringList(
        data=string_responses,
        count=len(string_responses),
        filters_applied=filters if any([
            is_palindrome, min_length, max_length,
            word_count, contains_character
        ]) else None
    )


@app.get("/strings/filter-by-natural-language", response_model=schemas.NaturalLanguageResponse)
def natural_language_filter(
    query: str = Query(..., description="Natural language query to filter strings"),
    db: Session = Depends(get_db)
):
    """
    Filter strings using natural language queries
    """
    try:
        filters = utils.parse_natural_language_query(query)
        
        db_query = db.query(models.StringAnalysis)
        
        if filters.is_palindrome is not None:
            db_query = db_query.filter(models.StringAnalysis.is_palindrome == filters.is_palindrome)
        
        if filters.min_length is not None:
            db_query = db_query.filter(models.StringAnalysis.length >= filters.min_length)
        
        if filters.max_length is not None:
            db_query = db_query.filter(models.StringAnalysis.length <= filters.max_length)
        
        if filters.word_count is not None:
            db_query = db_query.filter(models.StringAnalysis.word_count == filters.word_count)
        
        if filters.contains_character is not None:
            db_query = db_query.filter(
                models.StringAnalysis.value.contains(filters.contains_character)  # type: ignore
            )
        
        strings = db_query.all()
        
        string_responses = []
        for db_string in strings:
            db_dict = {c.name: getattr(db_string, c.name) for c in db_string.__table__.columns}
            
            properties = schemas.CharacterProperties(
                length=db_dict['length'],
                is_palindrome=db_dict['is_palindrome'],
                unique_characters=db_dict['unique_characters'],
                word_count=db_dict['word_count'],
                sha256_hash=db_dict['sha256_hash'],
                character_frequency_map=db_dict['character_frequency_map']
            )
            
            string_responses.append(
                schemas.StringAnalysis(
                    id=db_dict['id'],
                    value=db_dict['value'],
                    properties=properties,
                    created_at=db_dict['created_at']
                )
            )
        
        return schemas.NaturalLanguageResponse(
            data=string_responses,
            count=len(string_responses),
            interpreted_query=schemas.NaturalLanguageQuery(
                original=query,
                parsed_filters=filters
            )
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Query parsed but resulted in conflicting filters: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse natural language query: {str(e)}"
        )


@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    """
    Delete a string by its value
    """
    db_string = db.query(models.StringAnalysis).filter(
        models.StringAnalysis.value == string_value
    ).first()
    
    if db_string is None:
        raise HTTPException(
            status_code=404,
            detail="String does not exist in the system"
        )
    
    db.delete(db_string)
    db.commit()