
with source as (
    SELECT
        id,
        repo_id,
        title,
        is_pull_request,
        state,
        opened_at,
        closed_at
    FROM {{ source('github_activity_raw', 'issues') }}
),

cleaned as (
    SELECT
        id::string                as id,
        repo_id::string           as repo_id,
        title::string             as title,
        is_pull_request::boolean  as is_pull_request,
        state::string             as state,
        opened_at::timestamp      as opened_at,
        closed_at::timestamp      as closed_at
    FROM source
    ORDER BY opened_at DESC, closed_at DESC
)

select * from cleaned