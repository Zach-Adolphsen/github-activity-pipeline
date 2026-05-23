
with source as (
    select
        id,
        repo_id,
        author,
        committed_at
    from {{ source('github_activity_raw', 'commits') }}
),

cleaned as (
    select
        id::string                as id,
        repo_id::string           as repo_id,
        author::string            as author,
        committed_at::timestamp   as committed_at
    from source
    order by committed_at desc
)

select * from cleaned