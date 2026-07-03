"""Enrichment pipeline using the Strategy Pattern."""
import os
import sys
import json
import logging
from abc import ABC, abstractmethod
from google import genai
from google.genai import types  # pylint: disable=unused-import


class EnrichmentStrategy(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class defining the enrichment contract."""

    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Enrich a transcript record and return a structured dict."""

class LLMStrategy(ABC):  # pylint: disable=too-few-public-methods
    """Strict contract for LLM-based enrichment implementations."""

    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Invoke the LLM and return a validated structured dict."""


class ClaudeEnrichmentStrategy(LLMStrategy):  # pylint: disable=too-few-public-methods
    """Mock stub for Claude-based transcript enrichment."""

    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Return a hardcoded enrichment payload simulating Claude output."""
        return {
            "video_id": video_id,
            "cleaned_text": raw_text,
            "tech_terms": [],
            "book_names": []
        }


class GeminiEnrichmentStrategy(LLMStrategy):  # pylint: disable=too-few-public-methods
    """Concrete LLM strategy wrapping the Google Gemini API."""

    def __init__(self):
        """Initialize Gemini client and response schema from environment."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.critical("GEMINI_API_KEY missing. Cannot initialize GeminiEnrichmentStrategy.")
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)
        self.response_schema = {
            "type": "OBJECT",
            "properties": {
                "video_id": {"type": "STRING"},
                "cleaned_text": {"type": "STRING"},
                "tech_terms": {"type": "ARRAY", "items": {"type": "STRING"}},
                "book_names": {"type": "ARRAY", "items": {"type": "STRING"}}
            },
            "required": ["video_id", "cleaned_text"]
        }

    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Invoke Gemini API and return structured enrichment dict."""


class TranscriptEnricher:  # pylint: disable=too-few-public-methods
    """Orchestrates the enrichment stream processing loop."""

    def __init__(self, strategy: LLMStrategy):
        """Accept an enrichment strategy at construction time."""
        self.strategy = strategy

    def run(self, stream):
        """Process a line-by-line JSON stream and emit enriched records."""
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                video_id = record.get("video_id", "")
                raw_text = record.get("raw_text", "")
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Failed to parse record: %s", e)
                continue

            result = self.strategy.enrich(video_id, raw_text)
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()


def main():
    """Entry point: wire strategy into pipeline and run against stdin."""
    strategy = ClaudeEnrichmentStrategy()
    pipeline = TranscriptEnricher(strategy)
    pipeline.run(sys.stdin)


if __name__ == '__main__':
    main()
