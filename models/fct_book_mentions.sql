{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS book_title,
    INSERTED_AT AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }}
WHERE book_title IS NOT NULL
