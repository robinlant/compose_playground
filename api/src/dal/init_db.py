from psycopg2._psycopg import  cursor

def ensure_exists(cur: cursor) -> None:
    cur.execute("""
    BEGIN;
    
    CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(80) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    tag VARCHAR(80) NOT NULL,
    user_id SERIAL 
        REFERENCES users (id)
        ON DELETE CASCADE,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    anonymous_voting BOOLEAN NOT NULL DEFAULT FALSE,
    multiple_choice BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (user_id, tag)
    );
    
    CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY,
    text VARCHAR(80) NOT NULL,
    poll_id SERIAL
        REFERENCES polls (id)
        ON DELETE CASCADE,
    UNIQUE (text, poll_id)
    );
    
    CREATE TABLE IF NOT EXISTS votes (
    user_id SERIAL REFERENCES users (id),
    option_id SERIAL
        REFERENCES options (id)
        ON DELETE CASCADE,
    vote_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, option_id)
    );
    
    COMMIT;
    """)