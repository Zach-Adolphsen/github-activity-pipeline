import os

import duckdb
from dotenv import load_dotenv
from github import Auth, Github
import datetime as dt
from tqdm import tqdm

#=================================================================
#   Load environment variables and authenticate with GitHub API
#=================================================================
load_dotenv()
auth = Auth.Token(os.getenv("GITHUB_ACCESS_TOKEN"))

g = Github(base_url="https://api.github.com", auth=auth)

# Create database connection
con = duckdb.connect("github_activity_pipeline.db")

repos_to_load = ["donnemartin/system-design-primer",
                #  "supabase/supabase",
                "psf/black"
                ]

def get_issue_rows(repo, repo_id):
        issues_iter = repo.get_issues(state="all")
        issues_total = getattr(issues_iter, "totalCount", None)
        for issue in tqdm(issues_iter, desc=f"Issues for {repo_name}", total=issues_total, unit=" issue"):
            if issue.pull_request is None:
                yield (
                    repo_id,
                    issue.title,
                    False,  # is_pull_request
                    issue.state,
                    issue.created_at,
                    issue.closed_at,
                )
            else:
                yield (
                    repo_id,
                    issue.title,
                    True,  # is_pull_request
                    issue.state,
                    issue.created_at,
                    issue.closed_at,
                )

def get_commit_rows(repo, repo_id):
        commits_iter = repo.get_commits()
        commits_total = getattr(commits_iter, "totalCount", None)
        for c in tqdm(commits_iter, desc=f"Commits for {repo_name}", total=commits_total, unit=" commit"):
            author = c.commit.author.name
            committed_at = c.commit.author.date
            yield (repo_id, author, committed_at)


for repo_url in tqdm(repos_to_load, desc="Repos", unit=" repo"):
    con.execute("BEGIN TRANSACTION")
    
    rate = g.get_rate_limit().rate
    print(f"Rate limit: {rate.remaining}/{rate.limit} resets at {rate.reset}")
    print(f"Loading data for repo: {repo_url}")
    
    #=================================================================
    #   Get repo name and load into database
    #=================================================================
    print(f"Getting repo information for {repo_url}...")
    repo = g.get_repo(repo_url)
    repo_name = repo.name
    curr_dattime = dt.datetime.now()
    repo_author = repo.owner.login

    repo_id = None

    try:
        repo_id = con.execute(
            "INSERT OR IGNORE INTO repos (name, author, last_updated) VALUES (?, ?, ?) RETURNING id",
            [repo_name, repo_author, curr_dattime],
        ).fetchone()[0]
    except TypeError:
        print("Repo already exists in database, skipping insertion.")
        repo_id = con.execute(
            "SELECT id FROM repos WHERE name = ? and author = ?", [repo_name, repo_author]
        ).fetchone()[0]

    con.table("repos").show()
    
    #=================================================================
    #   Get repo commits and load into database
    #=================================================================
    print(f"Getting commits for {repo_url}...")

    con.executemany(
        """
            INSERT OR IGNORE INTO commits (repo_id, author, committed_at) VALUES (?, ?, ?)       
        """,
        get_commit_rows(repo, repo_id)
    )

    con.table("commits").show()

    #=================================================================
    #    Get forks and load into database
    #=================================================================
    print(f"Getting forks for {repo_url}...")
    num_of_forks = repo.forks_count
    print(f"Number of forks: {num_of_forks}")

    con.execute(
        """
            INSERT OR IGNORE INTO num_of_forks (repo_id, num_of_forks) VALUES (?, ?)
        """,
        [repo_id, num_of_forks],
    )

    con.table("num_of_forks").show()

    #=================================================================
    #    Get repo issues (including pull requests) and load into database
    #=================================================================
    print(f"Getting issues for {repo_url}...")

    con.executemany(
        """
            INSERT OR IGNORE INTO issues (repo_id, title, is_pull_request, state, opened_at, closed_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        get_issue_rows(repo, repo_id),
    )

    con.table("issues").show()


    #=================================================================
    #    Get repo stars and load into database
    #=================================================================
    print(f"Getting stars for {repo_url}...")
    num_stars = repo.stargazers_count

    con.execute(
        """
            INSERT OR IGNORE INTO stars (repo_id, num_of_stars) VALUES (?, ?)
        """,
        [repo_id, num_stars],
    )

    con.table("stars").show()


    # Update repo table with last_updated timestamp and close connection
    con.execute("UPDATE repos SET last_updated = ? WHERE id = ?",
        [dt.datetime.date(dt.datetime.now()), repo_id],
    )

    con.execute("COMMIT")

con.close()
