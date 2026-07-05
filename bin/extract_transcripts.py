#!/usr/bin/env python3
import sys
import os
import json
import logging
# TODO: Add the import statement so we have access to the load_dotenv function from dotenv
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Define absolute path structures to match the new layout
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH)

logging.basicConfig(
        filename=os.path.join(LOG_DIR, 'pipeline_audit.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
	logging.info("Pipeline Step 2A (Raw Extraction) started.")

	# Ingest routing keys from the local shell environment
	proxy_user = os.getenv("WEBSHARE_USER")
	proxy_pass = os.getenv("WEBSHARE_PASSWORD")

	if proxy_user and proxy_pass:
		logging.info("Proxy credentials detected. Routing traffic via Webshare Residential network.")
		# TODO:  Use YouTubeTranscriptApi with a keyword argument proxy_config.
		#    Use WebshareProxyConfig to create the proxy using the username and password
		ytt_api = YouTubeTranscriptApi(
			proxy_config=WebshareProxyConfig(proxy_username=proxy_user, proxy_password=proxy_pass)
		)
	else:
		logging.warning("No proxy credentials found. Running with direct raw local IP routing.")
		ytt_api = YouTubeTranscriptApi()

	# Process streaming IDs line-by-line from stdin
	for line in sys.stdin:
		video_id = line.strip()
		if not video_id:
			continue

		logging.info(f"Processing transcript extraction for video: {video_id}")

		try:
			# Execute the modern 2026 instance lookup method
			fetched_transcript = ytt_api.fetch(video_id)
			transcript_list = fetched_transcript.to_raw_data()

			# Stitch chunks with timestamp codes preserved for the staging file
			raw_text = " ".join([f"[{item['start']}] {item['text']}" for item in transcript_list])

			# Pack into a simple intermediary JSON object and emit to stdout
			# TODO: Create a variable called payload
			#    Store a dict object with video_id and raw_text as keys, with the appropriate values
			#    Then use sys.stdout to write that to console
			#    Finally, flush the stdout 
			payload = {
				"video_id": video_id,
				"raw_text": raw_text
			}
			sys.stdout.write(json.dumps(payload) + "\n")
			sys.stdout.flush()

		except Exception as e:
			logging.error(f"Failed to fetch YouTube transcript for {video_id}: {str(e)}")
			continue

	logging.info("Pipeline Step 2A finished.")

if __name__ == '__main__':
	main()
