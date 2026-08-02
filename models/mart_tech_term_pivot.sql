{{ config(materialized='table') }}

{% set tech_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    v.video_id,
    {% for term in tech_terms %}
    COUNT(CASE WHEN LOWER(t.tech_term) = '{{ term }}' THEN 1 END) AS {{ term }}_count{% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ ref('dim_videos') }} v
LEFT JOIN {{ ref('fct_tech_terms') }} t
    ON v.video_id = t.video_id
GROUP BY 1
