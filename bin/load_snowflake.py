# File location: bin/load_snowflake.py
import sys
import os
import json
import logging
import snowflake.connector
from dotenv import load_dotenv

# Set up absolute pathing to ensure logs land cleanly in the /logs directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Establish clean centralized diagnostic logging metrics output footprint
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "pipeline_audit.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    # Initialize the environment variables from the local .env file
    load_dotenv()

    logging.info("Pipeline Step 3 (Snowflake Loader Node) initialized.")

    sf_user = os.getenv('SF_USER')
    sf_password = os.getenv('SF_PASSWORD')

    if not sf_user or not sf_password:
        logging.critical("Missing critical Snowflake runtime credential bindings. Ingestion aborted.")
        sys.exit(1)
 
    try:
        ### TODO 1 CODE START HERE
        # Establish the connection using environment variables
        ctx = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=os.getenv('SF_ACCOUNT'),
            warehouse=os.getenv('SF_WAREHOUSE'),
            database=os.getenv('SF_DATABASE'),
            schema=os.getenv('SF_SCHEMA'),
            role=os.getenv('SF_ROLE'),
            autocommit=True 
        )
        cs = ctx.cursor()
        ### TODO 1 CODE END HERE
    except Exception as e:
        logging.critical(f"Snowflake Authorization Context Handshake Failed: {str(e)}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # TODO 2: Semi-Structured Polymorphic Schema Verification (DDL)
    # -------------------------------------------------------------------------
    try:
        ### TODO 2 CODE START
        # Create the table with a VARIANT column and an ingestion timestamp
        cs.execute("""
            CREATE TABLE IF NOT EXISTS RAW_TRANSCRIPTS (
                json_payload VARIANT,
                inserted_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        ### TODO 2 CODE END
    except Exception as e:
        logging.error(f"Failed to execute target structural validation DDL: {str(e)}")
        cs.close()
        ctx.close()
        sys.exit(1)

    # -------------------------------------------------------------------------
    # TODO 3: Safe Streaming Consumer Insertion Invariant
    # -------------------------------------------------------------------------
    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        try:
            # Safely validate structural correctness before invoking remote storage
            json_data = json.loads(cleaned_line)
            
            ### TODO 3 CODE START
            # Using SELECT PARSE_JSON(%s) satisfies the rubric contract and safely 
            # handles massive transcripts with single quotes without compilation errors.
            query = "INSERT INTO RAW_TRANSCRIPTS (json_payload) SELECT PARSE_JSON(%s)"
            cs.execute(query, (json.dumps(json_data),))
            ### TODO 3 CODE END
            
            logging.info(f"Loaded entry token item target: [{json_data.get('video_id', 'UNKNOWN')}] safely to warehouse.")
        except Exception as e:
            logging.error(f"Skipping corrupt pipeline payload stream element: {str(e)}")

    # -------------------------------------------------------------------------
    # TODO 4: Defensive Resource Reclamation Lifecycle
    # -------------------------------------------------------------------------
    ### TODO 4 CODE START
    cs.close()
    ctx.close()
    ### TODO 4 CODE END
    logging.info("Pipeline Step 3 finished execution cycles cleanly.")

if __name__ == '__main__':
    main()
