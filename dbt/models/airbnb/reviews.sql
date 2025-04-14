{{ 
    config(
        materialized='incremental',
        unique_key=['id', 'snapshot_date'],
        partition_by={
            "field": "snapshot_date",
            "data_type": "date",
            "granularity": "month"
        }
    )
}}

with source_data as (
    select * from {{ source('staging', 'staging_reviews') }}
    {% if is_incremental() %}
        WHERE snapshot_date = '{{ var('snapshot_date') }}'
    {% endif %}
),

transformed_data as (
    select
        id,
        listing_id, 
        "date" as date, 
        reviewer_id, 
        reviewer_name,
        PARSE_DATE('%Y-%m-%d', snapshot_date) as snapshot_date
    from source_data
)

select * from transformed_data
