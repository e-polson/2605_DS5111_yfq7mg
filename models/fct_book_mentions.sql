-- Step 3b - book mentions (dbt syntax)
{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS BOOK_TITLE,
    INSERTED_AT AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }},
LATERAL FLATTEN(input => BOOK_NAMES_ARRAY) f
