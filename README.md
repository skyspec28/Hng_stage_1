# Backend Wizards — Stage 1: String Analyzer Service

A FastAPI application that analyzes strings and stores their computed properties. The service provides comprehensive string analysis including length calculation, palindrome checking, unique character counting, and more.

## Features

- String length calculation
- Palindrome detection (case-insensitive)
- Unique character counting
- Word count analysis
- SHA-256 hash generation
- Character frequency mapping
- Natural language query filtering
- Comprehensive string property storage

## Prerequisites

- Python 3.8 or higher
- PostgreSQL

## Installation

1. Clone the repository:

```bash
git clone https://github.com/skyspec28/Hng_stage_1.git
cd Hng_stage_1
```

1. Create a virtual environment and activate it:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

1. The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`

## API Endpoints

### 1. Create/Analyze String

```http
POST /strings
Content-Type: application/json

{
  "value": "string to analyze"
}
```

#### Success Response (201 Created)

```json
{
  "id": "sha256_hash_value",
  "value": "string to analyze",
  "properties": {
    "length": 17,
    "is_palindrome": false,
    "unique_characters": 12,
    "word_count": 3,
    "sha256_hash": "abc123...",
    "character_frequency_map": {
      "s": 2,
      "t": 3,
      "r": 2
    }
  },
  "created_at": "2025-08-27T10:00:00Z"
}
```

#### Error Responses

- 409 Conflict: String already exists
- 400 Bad Request: Invalid request body
- 422 Unprocessable Entity: Invalid data type

### 2. Get Specific String

```http
GET /strings/{string_value}
```

Returns the analyzed string data with HTTP 200 OK or 404 Not Found if not exists.

### 3. Get All Strings with Filtering

```http
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
```

#### Query Parameters

- is_palindrome: boolean (true/false)
- min_length: integer
- max_length: integer
- word_count: integer
- contains_character: string

### 4. Natural Language Filtering

```http
GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings
```

Supports queries like:

- "all single word palindromic strings"
- "strings longer than 10 characters"
- "palindromic strings that contain the first vowel"
- "strings containing the letter z"

### 5. Delete String

```http
DELETE /strings/{string_value}
```

Returns 204 No Content on success or 404 Not Found if string doesn't exist.

## Example Usage

```bash
# Create/Analyze a string
curl -X POST "http://localhost:8000/strings" \
     -H "Content-Type: application/json" \
     -d '{"value": "Hello, World!"}'

# Get a specific string
curl -X GET "http://localhost:8000/strings/Hello%2C%20World%21"

# Get filtered strings
curl -X GET "http://localhost:8000/strings?is_palindrome=true&min_length=5"

# Natural language filter
curl -X GET "http://localhost:8000/strings/filter-by-natural-language?query=all%20palindromic%20strings"

# Delete a string
curl -X DELETE "http://localhost:8000/strings/Hello%2C%20World%21"
```

## License

This project is licensed under the MIT License.
