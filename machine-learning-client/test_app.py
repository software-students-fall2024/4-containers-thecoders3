"""
This module contains unit tests for ml-client.
"""

import io
from pathlib import Path
import pytest
import speech_recognition as sr

from app import app


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

    class MockAudioFile:
        """Mock class for AudioFile."""

        pass

    class MockRecognizer:
        def recognize_google(self, audio):
            return "Test transcription"

        def record(self, source):
            return MockAudioFile()  # Simulate recording audio

    class MockCollections:
        def insert_one(self, data):
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

    class MockAudioFile:
        """Mock class for AudioFile."""

        pass

    class MockRecognizer:
        def record(self, source):
            return MockAudioFile()  # Simulate recording audio

        def recognize_google(self, audio):
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

    class MockAudioFile:
        """Mock class for AudioFile."""

        pass

    class MockRecognizer:
        def record(self, source):
            return MockAudioFile()  # Simulate recording audio

        def recognize_google(self, audio):
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
