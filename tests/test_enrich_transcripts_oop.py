"""Tests for the OOP enrichment pipeline."""
import io
import json
from enrich_transcripts_oop import ClaudeEnrichmentStrategy, EnrichmentPipeline  # pylint: disable=import-error

def test_pipeline_emits_enriched_records(capsys):
    """Verify pipeline reads mock stdin and emits valid enriched JSON."""
    mock_input = {"video_id": "ds5111_v001", "raw_text": "00:01 Welcome to class."}
    mock_stdin = io.StringIO(json.dumps(mock_input) + "\n")

    strategy = ClaudeEnrichmentStrategy()
    pipeline = EnrichmentPipeline(strategy)
    pipeline.run(mock_stdin)

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1
    parsed = json.loads(stdout_lines[0])
    assert parsed["video_id"] == "ds5111_v001"
    assert "tech_terms" in parsed
    assert "book_names" in parsed
