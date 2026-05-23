
with source as (
    select
        id,
        repo_id,
        num_of_stars,
        inserted_at
    from {{ source('github_activity_raw', 'stars') }}
),

cleaned as (
    select
        id::string                as id,
        repo_id::string           as repo_id,
        num_of_stars::integer     as num_of_stars,
        inserted_at::timestamp    as inserted_at
    from source
    ORDER BY inserted_at DESC
)

select * from cleaned