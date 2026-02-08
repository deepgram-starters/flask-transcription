"""
Flask Transcription Starter - Backend Server

This is a simple Flask server that provides a transcription API endpoint
powered by Deepgram's Speech-to-Text service. It's designed to be easily
modified and extended for your own projects.

Key Features:
- Single API endpoint: POST /api/transcription
- Accepts both file uploads and URLs
- Serves built frontend from frontend/dist/
- CORS enabled for development
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from deepgram import DeepgramClient
from dotenv import load_dotenv

# Load .env without overriding existing env vars
load_dotenv(override=False)

# ============================================================================
# CONFIGURATION - Customize these values for your needs
# ============================================================================

# Default transcription model to use when none is specified
# Options: "nova-3", "nova-2", "nova", "enhanced", "base"
# See: https://developers.deepgram.com/docs/models-languages-overview
DEFAULT_MODEL = "nova-3"

# Server configuration
CONFIG = {
    "port": int(os.environ.get("PORT", 8081)),
    "host": os.environ.get("HOST", "0.0.0.0"),
}

# ============================================================================
# API KEY LOADING - Load Deepgram API key from .env
# ============================================================================

def load_api_key():
    """
    Loads the Deepgram API key from environment variables
    Priority: DEEPGRAM_API_KEY env var > error
    """
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not api_key:
        print("\n❌ ERROR: Deepgram API key not found!\n")
        print("Please set your API key using one of these methods:\n")
        print("1. Create a .env file (recommended):")
        print("   DEEPGRAM_API_KEY=your_api_key_here\n")
        print("2. Environment variable:")
        print("   export DEEPGRAM_API_KEY=your_api_key_here\n")
        print("Get your API key at: https://console.deepgram.com\n")
        raise ValueError("DEEPGRAM_API_KEY environment variable is required")

    return api_key

api_key = load_api_key()

# ============================================================================
# SETUP - Initialize Flask, Deepgram, and middleware
# ============================================================================

# Initialize Deepgram client with API key
deepgram = DeepgramClient(api_key=api_key)

# Initialize Flask app (API server only)
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app)

# ============================================================================
# HELPER FUNCTIONS - Modular logic for easier understanding and testing
# ============================================================================

def validate_transcription_input(file, url):
    """
    Validates that either a file or URL was provided in the request

    Args:
        file: Flask file object from request.files
        url: URL string from request.form

    Returns:
        dict: Input type and data, or None if invalid
    """
    # URL-based transcription
    if url:
        return {"type": "url", "data": url}

    # File-based transcription
    if file:
        return {"type": "file", "data": file}

    # Neither provided
    return None

def transcribe_audio(input_data, model=DEFAULT_MODEL):
    """
    Sends a transcription request to Deepgram

    Args:
        input_data: dict with 'type' and 'data' keys
        model: Model name to use (e.g., "nova-3")

    Returns:
        dict: Deepgram API response
    """
    # URL transcription
    if input_data["type"] == "url":
        response = deepgram.listen.v1.media.transcribe_url(
            url=input_data["data"],
            model=model,
            smart_format=True,
        )
        return response

    # File transcription
    file_obj = input_data["data"]
    file_content = file_obj.read()

    response = deepgram.listen.v1.media.transcribe_file(
        request=file_content,
        model=model,
        smart_format=True,
    )
    return response

def format_transcription_response(transcription_response, model_name):
    """
    Formats Deepgram's response into the starter contract format

    Args:
        transcription_response: Raw Deepgram API response
        model_name: Name of model used for transcription

    Returns:
        dict: Formatted response matching the STT contract
    """
    # Access the results from the Deepgram response
    result = transcription_response.results.channels[0].alternatives[0]
    metadata = transcription_response.metadata

    if not result:
        raise ValueError("No transcription results returned from Deepgram")

    # Build response object matching the contract
    response = {
        "transcript": result.transcript or "",
    }

    # Add optional fields if available
    if hasattr(result, 'words') and result.words:
        response["words"] = [
            {
                "text": word.word,
                "start": word.start,
                "end": word.end,
                "speaker": word.speaker if hasattr(word, 'speaker') else None
            }
            for word in result.words
        ]

    if metadata and hasattr(metadata, 'duration'):
        response["duration"] = metadata.duration

    # Add metadata
    response["metadata"] = {
        "model_uuid": metadata.model_uuid if hasattr(metadata, 'model_uuid') else None,
        "request_id": metadata.request_id if hasattr(metadata, 'request_id') else None,
        "model_name": model_name,
    }

    return response

def format_error_response(error, status_code=500):
    """
    Formats error responses in a consistent structure per the contract
    """
    # Map status codes to error responses
    if status_code == 400:
        error_type = "ValidationError"
        error_code = "INVALID_INPUT"
        safe_message = "The request is invalid. Please check your input and try again."
    else:
        error_type = "TranscriptionError"
        error_code = "TRANSCRIPTION_FAILED"
        safe_message = "Transcription failed. Please try again."

    return {
        "error": {
            "type": error_type,
            "code": error_code,
            "message": safe_message,
        }
    }, status_code

# ============================================================================
# API ROUTES - Define your API endpoints here
# ============================================================================

@app.route("/api/transcription", methods=["POST"])
def transcribe():
    """
    POST /api/transcription

    Main transcription endpoint. Accepts either:
    - A file upload (multipart/form-data with 'file' field)
    - A URL to audio file (form data with 'url' field)

    Optional parameters:
    - model: Deepgram model to use (default: "nova-3")

    Returns:
        JSON response matching the STT contract:
        {
            "transcript": "transcribed text...",
            "words": [...],  # optional
            "duration": 123.45,  # optional
            "metadata": {...}
        }
    """
    try:
        # Extract file and URL from request
        file = request.files.get("file")
        url = request.form.get("url")
        model = request.form.get("model", DEFAULT_MODEL)

        # Validate input - must have either file or URL
        input_data = validate_transcription_input(file, url)

        if not input_data:
            error_response, status = format_error_response(
                ValueError("Either 'file' or 'url' must be provided"),
                400
            )
            return jsonify(error_response), status

        # Transcribe the audio
        transcription_response = transcribe_audio(input_data, model)

        # Format and return the response
        formatted_response = format_transcription_response(
            transcription_response,
            model
        )

        return jsonify(formatted_response), 200

    except ValueError as e:
        # Validation errors (400)
        error_response, status = format_error_response(e, 400)
        return jsonify(error_response), status

    except Exception as e:
        # Transcription errors (500)
        print(f"Transcription error: {e}")
        error_response, status = format_error_response(e, 500)
        return jsonify(error_response), status

@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    """
    GET /api/metadata

    Returns metadata about this starter application from deepgram.toml
    Required for standardization compliance
    """
    try:
        import toml
        with open('deepgram.toml', 'r') as f:
            config = toml.load(f)

        if 'meta' not in config:
            return jsonify({
                'error': 'INTERNAL_SERVER_ERROR',
                'message': 'Missing [meta] section in deepgram.toml'
            }), 500

        return jsonify(config['meta']), 200

    except FileNotFoundError:
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': 'deepgram.toml file not found'
        }), 500

    except Exception as e:
        print(f"Error reading metadata: {e}")
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': f'Failed to read metadata from deepgram.toml: {str(e)}'
        }), 500

# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":
    port = CONFIG["port"]
    host = CONFIG["host"]
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("\n" + "=" * 70)
    print(f"🚀 Flask Transcription Server (Backend API)")
    print("=" * 70)
    print(f"🚀 Backend API Server running at http://localhost:{port}")
    print(f"")
    print(f"📡 POST /api/transcription")
    print(f"📡 GET  /api/metadata")
    print(f"Debug:    {'ON' if debug else 'OFF'}")
    print("=" * 70 + "\n")

    app.run(host=host, port=port, debug=debug)
