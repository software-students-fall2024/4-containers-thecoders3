"""
This module contains unit tests for ml-client.
"""

import io
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import speech_recognition as sr
# from flask import Flask
from app import app


@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


# @patch("app.sr.Recognizer")
def test_transcribe_no_audio(client):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with no audio file provided."""
    response = client.post("/transcribe", content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "No audio file provided",
    }


@patch("app.collections")
@patch("app.sr.Recognizer")
def test_transcribe_success(
    mock_recognizer, mock_collections, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with a successful transcription."""
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.return_value = "Test transcription"
    mock_collections.insert_one.return_value.inserted_id = "mock_id"

    wav_file_path = Path(__file__).parent / "wav_example.wav"
    with open(wav_file_path, "rb") as f:
        audio_content = io.BytesIO(f.read())
    audio_content.name = "test_audio.wav"

    response = client.post(
        "/transcribe",
        data={"audio": (audio_content, "test_audio.wav")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "id": "mock_id",
    }


@patch("app.sr.Recognizer")
def test_transcribe_request_error(
    mock_recognizer, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with a request error from the recognizer."""
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.side_effect = sr.RequestError(
        "Mock error"
    )

    wav_file_path = Path(__file__).parent / "wav_example.wav"
    with open(wav_file_path, "rb") as f:
        audio_content = io.BytesIO(f.read())
    audio_content.name = "test_audio.wav"

    response = client.post(
        "/transcribe",
        data={"audio": (audio_content, "test_audio.wav")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "Could not request results from Google Speech Recognition service Mock error",
    }


@patch("app.sr.Recognizer")
def test_transcribe_unknown_value_error(
    mock_recognizer, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with an unrecognizable audio file."""
    mock_recognizer_instance = MagicMock()
    mock_recognizer.return_value = mock_recognizer_instance
    mock_recognizer_instance.recognize_google.side_effect = sr.UnknownValueError()

    wav_file_path = Path(__file__).parent / "wav_example.wav"
    with open(wav_file_path, "rb") as f:
        audio_content = io.BytesIO(f.read())
    audio_content.name = "test_audio.wav"

    response = client.post(
        "/transcribe",
        data={"audio": (audio_content, "test_audio.wav")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "Could not understand audio",
    }
