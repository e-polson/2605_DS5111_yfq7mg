"""Unit test suite validating the streaming transcript enrichment pipeline."""

import io
import json
import os
import sys

# Append root folder context pathing to resolve import paths smoothly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=wrong-import-position, import-error
from google.genai.models import Models

from bin.enrich_transcripts import main


class MockGeminiResponse:  # pylint: disable=too-few-public-methods
    """Dummy container mimicking the Gemini SDK response hierarchy."""

    def __init__(self, text_payload):
        """Initialize with predefined text output."""
        self.text = text_payload


def test_enrich_transcripts_streaming_pipeline(monkeypatch, capsys):
    """Verifies that main() reads mock lines from stdin, calls the Gemini client

    structure, and streams verified JSON objects out to stdout without making
    live API network requests.
    """

    # Prefix unused arguments with an underscore to clear W0613 warnings cleanly
    def mock_generate_content(_self, model, contents, config=None):
        """Pre-baked, schema-compliant JSON string mimicking model output."""
	# pylint: disable=unused-argument
        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": "Welcome to class. Today we are testing mock frameworks.",
            "tech_terms": ["mock frameworks"],
            "book_names": [],
        }
        return MockGeminiResponse(json.dumps(mock_data))

    monkeypatch.setattr(Models, "generate_content", mock_generate_content)

    # Simulate your stream input pipeline using an in-memory text buffer
    mock_input_row = {
        "video_id": "ds5111_v001",
        "raw_text": "00:01 Welcome to class. Today we are testing mock frameworks.",
    }
    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    # Trigger the main pipeline script execution loop
    main()

    # Intercept the standard console text buffers
    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    # Execute data integrity validation assertions
    assert len(stdout_lines) == 1
    parsed_output = json.loads(stdout_lines[0])
    assert parsed_output["video_id"] == "ds5111_v001"
    assert "mock frameworks" in parsed_output["tech_terms"]
