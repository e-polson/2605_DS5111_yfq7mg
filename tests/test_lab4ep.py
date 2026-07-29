"""Tests for checking raw transcript extraction pipeline streaming operations."""

import io
import os
import sys
import json

# Inject root paths so test scripts can discover library utilities seamlessly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

# pylint: disable=wrong-import-position, import-error
from youtube_transcript_api import YouTubeTranscriptApi
from extract_transcripts import main


class MockTranscriptContainer:  # pylint: disable=too-few-public-methods
    """Mimics the .to_raw_data() array output return schema"""

    def to_raw_data(self):
        """Mock return array matching extraction requirements."""
        return [{"start": 10.5, "text": "Automated container tracking loop text entry."}]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """Verifies that the main() entrypoint loop correctly processes video IDs

    via stdin and outputs structured JSON Lines objects via stdout without
    hitting the internet.
    """

    # Prefix unused args with an underscore to clear W0613 warnings cleanly
    def stubbed_fetch_route(_self, _video_id):
        return MockTranscriptContainer()

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # Mock Standard Input (sys.stdin) to feed a fake video ID into your script
    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # Trigger your script's main entry point execution loop directly
    main()

    # Intercept the standard console terminal print buffers using capsys
    captured_output = capsys.readouterr()

    # Clean up trailing whitespace and isolate rows
    stdout_lines = captured_output.out.strip().split("\n")

    # Execute structural validations against the emitted JSON Lines payload contract
    assert len(stdout_lines) == 1, (
        "The pipeline loop should emit exactly one row per valid input ID."
    )

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_transcripts_error_handling_and_continuation(monkeypatch, capsys):
    """Verifies that when an invalid, empty, or un-fetchable video ID hits

    the stream, the script catches the error gracefully, logs it, avoids
    crashing, and successfully continues processing subsequent valid video IDs.
    """

    # Changed generic Exception to a precise RuntimeError to fix W0719 rule
    def stubbed_fetch_route_with_error(_self, video_id):
        if video_id == "unfetchable_video_123":
            raise RuntimeError("Transcript disabled or video not found")
        return MockTranscriptContainer()

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route_with_error)

    # Mock Standard Input with a broken ID followed immediately by a valid ID.
    mock_input_stream = io.StringIO("unfetchable_video_123\nfake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # Trigger your script's main entry point execution loop directly
    main()

    # Intercept standard console outputs
    captured_output = capsys.readouterr()
    stdout_lines = [line for line in captured_output.out.strip().split("\n") if line]

    # Execute structural validations
    assert len(stdout_lines) == 1, (
        "The pipeline should gracefully skip the failed ID and emit exactly "
        "1 row for the valid ID."
    )

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999", (
        "The pipeline failed to continue onto the valid video ID."
    )
    assert "Automated container tracking" in parsed_json_line["raw_text"]
