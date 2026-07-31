{{ config(materialized='table') }}

-- 1. Define the list of terms to pivot
{% set core_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    video_id,
    
    -- 2. Dynamically loop through terms to build aggregate columns
    {% for term in core_terms %}
    
    SUM(CASE WHEN LOWER(term_name) = '{{ term }}' THEN 1 ELSE 0 END) AS count_{{ term }}_mentions
    
    {% if not loop.last %},{% endif %}
    
    {% endfor %}

FROM {{ ref('fct_tech_terms') }}
GROUP BY video_id
