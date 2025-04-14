{{ 
    config(materialized='table')
}}

with source_data as (
    select * from {{ source('staging', 'staging_listings') }}
),

renamed_data as (
    select distinct
        host_id as id,
        host_url as url,
        host_name as name,
        host_since as since,
        host_location as location,
        host_about as about,
        host_response_time as response_time,
        host_response_rate as response_rate,
        host_acceptance_rate as acceptance_rate,
        host_is_superhost as is_superhost,
        host_thumbnail_url as thumbnail_url,
        host_picture_url as picture_url,
        host_neighbourhood as neighbourhood,
        host_listings_count as listings_count,
        host_total_listings_count as total_listings_count,
        host_verifications as verifications,
        host_has_profile_pic as has_profile_pic,
        host_identity_verified as identity_verified,
    from source_data
)

select * from renamed_data
