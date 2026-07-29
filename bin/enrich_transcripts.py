"""Module for processing and enriching raw text transcripts using the Gemini AI API."""

#!/usr/bin/env python3
import json
import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Define explicit project layout structural directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Correct pathing context to look for the .env file in the project root directory
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# Audit logging framework tracking pipeline telemetry safely inside /logs
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "pipeline_audit.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    """Reads raw transcripts from stdin and enriches them via the Gemini API."""
    logging.info("Pipeline Step 2B (Gemini Enrichment) started.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical(
            "GEMINI_API_KEY environment variable evaluates to None. Hard programmatic exit."
        )
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    response_schema = {
        "type": "OBJECT",
        "properties": {"video_id": {"type": "STRING"}, "cleaned_text": {"type": "STRING"}},
        "required": ["video_id", "cleaned_text"],
    }

    # Stream processing framework reading line-by-line text inputs from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            # EXTLocal parsing steps mapping inputs
            record = json.loads(line)
            video_id = record.get("video_id", "")
            raw_text = record.get("raw_text", "")
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Failed to parse incoming JSON payload row: %s", err)
            continue

        logging.info("Orchestrating Gemini enrichment for video: %s", video_id)

        prompt = f"""
        You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
        1. Strip all timestamps and duration codes.
        2. Extract technical architecture terms and books.
        """

        try:
            # INVOCATION AND EMISSION PATTERN HERE
            full_prompt = f"{prompt}\n\nRaw Text Sequence:\n{raw_text}"

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1,
                ),
            )

            sys.stdout.write(response.text + "\n")
            sys.stdout.flush()

        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error(
                "Failed processing video %s during LLM generation: %s", video_id, err
            )

    logging.info("Pipeline Step 2B finished.")


if __name__ == "__main__":
    main()
