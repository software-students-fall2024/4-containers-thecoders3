"""
This module contains unit tests for ml-client.
"""
# pylint: disable=wrong-import-position
import io
import warnings
from pathlib import Path

import speech_recognition as sr

from app import app

warnings.filterwarnings("ignore", category=DeprecationWarning)
import pytest


@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


def test_transcribe_no_audio(client):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with no audio file provided."""
    response = client.post("/transcribe", content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "No audio file provided",
    }


def test_transcribe_success(
    monkeypatch, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with a successful transcription."""

    class MockAudioFile:  # pylint: disable=too-few-public-methods
        """Mock class for AudioFile."""

    class MockRecognizer:
        """Mock class to simulate the behavior of sr.Recognizer."""

        def recognize_google(self, audio):  # pylint: disable=unused-argument
            """Simulate recording audio from a source."""
            return "Test transcription"

        def record(self, source):  # pylint: disable=unused-argument
            """Simulate recognizing audio using Google API."""
            return MockAudioFile()  # Simulate recording audio

    class MockCollections:  # pylint: disable=too-few-public-methods
        """Mock class to simulate a MongoDB collection."""

        def insert_one(self, data):  # pylint: disable=unused-argument
            """Simulate inserting data into a collection."""
            return type("MockResult", (), {"inserted_id": "mock_id"})()

    monkeypatch.setattr("app.sr.Recognizer", MockRecognizer)
    monkeypatch.setattr("app.collections", MockCollections())

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


def test_transcribe_request_error(
    monkeypatch, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with a request error from the recognizer."""

    class MockAudioFile:  # pylint: disable=too-few-public-methods
        """Mock class for AudioFile."""

    class MockRecognizer:
        """Mock class to simulate the behavior of sr.Recognizer."""

        def record(self, source):  # pylint: disable=unused-argument
            """Simulate recording audio from a source."""
            return MockAudioFile()  # Simulate recording audio

        def recognize_google(self, audio):  # pylint: disable=unused-argument
            """Simulate recognizing audio using Google API."""
            raise sr.RequestError("Mock error")

    monkeypatch.setattr("app.sr.Recognizer", MockRecognizer)

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


def test_transcribe_unknown_value_error(
    monkeypatch, client
):  # pylint: disable=redefined-outer-name
    """Test the /transcribe endpoint with an unrecognizable audio file."""

    class MockAudioFile:  # pylint: disable=too-few-public-methods
        """Mock class for AudioFile."""

    class MockRecognizer:
        """Mock class to simulate the behavior of sr.Recognizer."""

        def record(self, source):  # pylint: disable=unused-argument
            """Simulate recording audio from a source."""
            return MockAudioFile()  # Simulate recording audio

        def recognize_google(self, audio):  # pylint: disable=unused-argument
            """Simulate recognizing audio using Google API."""
            raise sr.UnknownValueError()

    monkeypatch.setattr("app.sr.Recognizer", MockRecognizer)

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
