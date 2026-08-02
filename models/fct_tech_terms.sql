{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    LOWER(TRIM(f.value::STRING)) AS tech_term,
    INSERTED_AT AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }},
LATERAL FLATTEN(input => TECH_TERMS_ARRAY) f
WHERE f.value IS NOT NULL 
  AND TRIM(f.value::STRING) != ''
