{{ config(materialized='table') }}

{% set core_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    v.video_id,
    
    {% for term in core_terms %}
    COALESCE(SUM(CASE WHEN LOWER(t.tech_term) = '{{ term }}' THEN 1 ELSE 0 END), 0) AS count_{{ term }}_mentions{% if not loop.last %},{% endif %}
    {% endfor %}

FROM {{ ref('dim_videos') }} v
LEFT JOIN {{ ref('fct_tech_terms') }} t
    ON v.video_id = t.video_id
GROUP BY 1
