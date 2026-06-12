import sys
import io
import json
import pytest
from youtube_transcript_api import YouTubeTranscriptApi

# Import the executable main entry point loop from your pipeline package directory
from extract_transcripts import main

class MockTranscriptContainer:
    """Mimics the 2026 .to_raw_data() array output return schema"""
    def to_raw_data(self):
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]

def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """
    Verifies that the main() entrypoint loop correctly processes video IDs via stdin
    and outputs structured JSON Lines objects via stdout without hitting the internet.
    """
    # 1. Mock the external third-party API fetch dependency
    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    # 2. Mock Standard Input (sys.stdin) to feed a fake video ID into your script
    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Trigger your script's main entry point execution loop directly
    main()

    # 4. Intercept the standard console terminal print buffers using capsys
    captured_output = capsys.readouterr()

    # Clean up trailing whitespace and isolate rows
    stdout_lines = captured_output.out.strip().split("\n")

    # 5. Execute structural validations against the emitted JSON Lines payload contract
    assert len(stdout_lines) == 1, "The pipeline loop should emit exactly one row per valid input ID."

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]

def test_extract_transcripts_error_handling_and_continuation(monkeypatch, capsys):
    """
    Verifies that when an invalid, empty, or un-fetchable video ID hits the stream,
    the script catches the error gracefully, logs it, avoids crashing, and 
    successfully continues processing subsequent valid video IDs in the stream.
    """
    # 1. Mock the fetch dependency to throw an error for a specific bad ID, but pass for others
    def stubbed_fetch_route_with_error(self, video_id):
        if video_id == "unfetchable_video_123":
            raise Exception("Transcript disabled or video not found")
        return MockTranscriptContainer()

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route_with_error)

    # 2. Mock Standard Input with a broken ID followed immediately by a valid ID.
    # This proves the loop catches errors gracefully and continues iterating.
    mock_input_stream = io.StringIO("unfetchable_video_123\nfake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    # 3. Trigger your script's main entry point execution loop directly
    main()

    # 4. Intercept standard console outputs
    captured_output = capsys.readouterr()
    stdout_lines = [line for line in captured_output.out.strip().split("\n") if line]

    # 5. Execute structural validations
    # The bad ID should be caught by your try/except block, meaning nothing is emitted to stdout for it.
    # The loop should continue and still emit a row for 'fake_video_999'.
    assert len(stdout_lines) == 1, "The pipeline should gracefully skip the failed ID and emit exactly 1 row for the valid ID."

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999", "The pipeline failed to continue onto the valid video ID."
    assert "Automated container tracking" in parsed_json_line["raw_text"]
