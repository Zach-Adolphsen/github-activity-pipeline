# create the database and tables
import duckdb as duck

con = duck.connect('github_activity_pipeline.db')

con.execute("drop table if exists stars")
con.execute("drop table if exists issues")
con.execute("drop table if exists commits")
con.execute("drop table if exists num_of_forks")
con.execute("drop table if exists repos")


con.sql("""
        CREATE TABLE IF NOT EXISTS repos (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            name VARCHAR(255) UNIQUE NOT NULL,
            author VARCHAR(255) NOT NULL,
            last_updated TIMESTAMP NOT NULL,
        )
""")

con.sql("""
        CREATE TABLE IF NOT EXISTS stars (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            repo_id UUID NOT NULL,
            num_of_stars INTEGER NOT NULL,
            inserted_at TIMESTAMP NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY (repo_id) REFERENCES repos(id),
            UNIQUE (repo_id, inserted_at)
        )
""")

con.sql("""
        CREATE TABLE IF NOT EXISTS issues (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            repo_id UUID NOT NULL,
            title VARCHAR(255) NOT NULL,
            is_pull_request BOOLEAN NOT NULL,
            state VARCHAR(255) NOT NULL,
            opened_at TIMESTAMP NOT NULL,
            closed_at TIMESTAMP,
            FOREIGN KEY (repo_id) REFERENCES repos(id)
        )
""")

con.sql("""
        CREATE TABLE if NOT EXISTS commits (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            repo_id UUID NOT NULL,
            author VARCHAR(255) NOT NULL,
            committed_at TIMESTAMP NOT NULL,
            UNIQUE (repo_id, author, committed_at),
            FOREIGN KEY (repo_id) REFERENCES repos(id)
        )
""")

con.sql("""
        CREATE TABLE if NOT EXISTS num_of_forks (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            repo_id UUID NOT NULL,
            num_of_forks INTEGER NOT NULL,
            inserted_at TIMESTAMP NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY (repo_id) REFERENCES repos(id),
            UNIQUE (repo_id, inserted_at)
        )
        
""")

con.close()

