"""
Flask Transcription Starter - Backend Server

This is a simple Flask server that provides a transcription API endpoint
powered by Deepgram's Speech-to-Text service. It's designed to be easily
modified and extended for your own projects.

Key Features:
- Single API endpoint: POST /stt/transcribe
- Accepts both file uploads and URLs
- Serves built frontend from frontend/dist/
- CORS enabled for development
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION - Customize these values for your needs
# ============================================================================

# Default transcription model to use when none is specified
# Options: "nova-3", "nova-2", "nova", "enhanced", "base"
# See: https://developers.deepgram.com/docs/models-languages-overview
DEFAULT_MODEL = "nova-3"

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

# Initialize Deepgram client
deepgram = DeepgramClient(api_key)

# Initialize Flask app - serve built frontend from frontend/dist/
app = Flask(__name__, static_folder="./frontend/dist", static_url_path="/")

# Enable CORS for all routes (needed for development with Vite)
# In production, you may want to restrict this to specific origins
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
    options = PrerecordedOptions(
        model=model,
        smart_format=True,
    )

    # URL transcription
    if input_data["type"] == "url":
        url_source = {"url": input_data["data"]}
        response = deepgram.listen.rest.v("1").transcribe_url(url_source, options)
        return response

    # File transcription
    file_obj = input_data["data"]
    file_content = file_obj.read()

    payload = FileSource(
        buffer=file_content
    )

    response = deepgram.listen.rest.v("1").transcribe_file(
        payload,
        options
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

    Args:
        error: The error that occurred
        status_code: HTTP status code to return

    Returns:
        tuple: (response_dict, status_code)
    """
    error_type = "ValidationError" if status_code == 400 else "TranscriptionError"

    # Determine error code based on error message
    error_message = str(error)
    if "url" in error_message.lower() or "invalid" in error_message.lower():
        error_code = "INVALID_URL"
    elif "audio" in error_message.lower():
        error_code = "BAD_AUDIO"
    elif "missing" in error_message.lower():
        error_code = "MISSING_INPUT"
    else:
        error_code = "TRANSCRIPTION_FAILED"

    return {
        "error": {
            "type": error_type,
            "code": error_code,
            "message": error_message,
            "details": {
                "originalError": str(error)
            }
        }
    }, status_code

# ============================================================================
# API ROUTES - Define your API endpoints here
# ============================================================================

@app.route("/")
def index():
    """Serve the main frontend HTML file"""
    return app.send_static_file("index.html")

@app.route("/stt/transcribe", methods=["POST"])
def transcribe():
    """
    POST /stt/transcribe

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

# ============================================================================
# FRONTEND STATIC FILES - Serve the built frontend
# ============================================================================

# Flask automatically serves static files from the static_folder
# No additional route needed - just ensure frontend/dist/ exists

# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    print("\n" + "=" * 70)
    print(f"🚀 Flask Transcription Server running at http://localhost:{port}")
    print(f"📦 Serving built frontend from frontend/dist")
    print("=" * 70 + "\n")

    app.run(host=host, port=port, debug=True)
