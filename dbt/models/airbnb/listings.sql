{{ 
    config(
        materialized='table',
        cluster_by = 'neighbourhood'
    )
}}

with source_data as (
    select * from {{ source('staging', 'staging_listings') }}
),

deduplicated_data as (
    select
        id,
        name,
        description,
        listing_url,
        neighbourhood_cleansed as neighbourhood
    from (
        select 
            id,
            name,
            description,
            listing_url,
            neighbourhood_cleansed,
            snapshot_date,
            row_number() over (partition by id order by snapshot_date desc) as rn
        from source_data
    ) ranked
    where rn = 1
)

select * from deduplicated_data
