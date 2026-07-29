"""Tests for the OOP enrichment pipeline."""

import io
import json
import os
import sys

# Inject root paths so pytest can discover local files when executing from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

# pylint: disable=wrong-import-position, import-error
from enrich_transcripts_oop import ClaudeEnrichmentStrategy, TranscriptEnricher, LLMStrategy

def test_pipeline_emits_enriched_records(capsys):
    """Verify pipeline reads mock stdin and emits valid enriched JSON."""
    mock_input = {"video_id": "ds5111_v001", "raw_text": "00:01 Welcome to class."}
    mock_stdin = io.StringIO(json.dumps(mock_input) + "\n")

    strategy = ClaudeEnrichmentStrategy()
    pipeline = TranscriptEnricher(strategy)
    pipeline.run(mock_stdin)

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1
    parsed = json.loads(stdout_lines[0])
    assert parsed["video_id"] == "ds5111_v001"
    assert "tech_terms" in parsed
    assert "book_names" in parsed

def test_orchestrator_with_mock_llm_strategy():
    """Verify TranscriptEnricher works with any LLMStrategy implementation."""

    class MockLLMStrategy(LLMStrategy):  # pylint: disable=too-few-public-methods
        """Inline mock strategy for isolated orchestrator testing."""

        def enrich(self, video_id: str, _raw_text: str) -> dict:
            """Return a fully controlled test payload."""
            return {
                "video_id": video_id,
                "cleaned_text": "Mock cleaned text.",
                "tech_terms": ["dbt", "Snowflake"],
                "book_names": ["Designing Data-Intensive Applications"],
            }

    mock_input = {"video_id": "ds5111_v001", "raw_text": "00:01 Welcome to class."}
    mock_stdin = io.StringIO(json.dumps(mock_input) + "\n")

    strategy = MockLLMStrategy()
    pipeline = TranscriptEnricher(strategy)
    pipeline.run(mock_stdin)
