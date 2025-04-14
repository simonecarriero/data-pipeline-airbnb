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
    select * from {{ source('staging', 'staging_listings') }}
    {% if is_incremental() %}
        WHERE snapshot_date = '{{ var('snapshot_date') }}'
    {% endif %}
),

transformed_data as (
    select
        id as listing_id,
        -- Transform price from VARCHAR "$137.00" to NUMERIC
        cast(replace(replace(price, '$', ''), ',', '') as NUMERIC) as price,
        PARSE_DATE('%Y-%m-%d', snapshot_date) as snapshot_date
    from source_data
)

select * from transformed_data
