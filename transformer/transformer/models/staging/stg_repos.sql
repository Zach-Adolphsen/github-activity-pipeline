
with source as (
    select
        id,
        name,
        author,
        last_updated
    from {{ source('github_activity_raw', 'repos') }}
),

cleaned as (
    select
        id::string                as id,
        name::string              as name,
        author::string            as author,
        last_updated::timestamp   as last_updated
    from source
)

select * from cleaned