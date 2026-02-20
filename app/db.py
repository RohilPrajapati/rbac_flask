from app.config import DB_CONFIG
from psycopg2 import pool
from contextlib import contextmanager

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

connection_pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)


@contextmanager
def get_connection():
    """
    Get connection from pool.
    Does NOT commit automatically.
    Caller is responsible for commit/rollback.
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    finally:
        if conn:
            connection_pool.putconn(conn)


# def get_connection():
#     return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # --- Create ENUM types ---
            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
                    CREATE TYPE gender_enum AS ENUM ('m','f','o');
                END IF;
            END$$;
            """)

            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                    CREATE TYPE user_role AS ENUM ('super_admin','artist_manager','artist');
                END IF;
            END$$;
            """)

            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'genre_enum') THEN
                    CREATE TYPE genre_enum AS ENUM ('rnb','country','classic','rock','jazz');
                END IF;
            END$$;
            """)

            # --- Users table ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                dob DATE NOT NULL,
                gender gender_enum NOT NULL,
                address VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                role user_role NOT NULL
            );
            """)
            print("Created User Table")

            # --- Artist table ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS artist (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                dob DATE NOT NULL,
                gender gender_enum NOT NULL,
                address VARCHAR(255) NOT NULL,
                first_release_year INT NULL,
                no_of_albums INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                user_id INT NULL,
                CONSTRAINT fk_artist_user
                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            """)
            print("Created Artist Table")

            # --- Music table ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS music (
                id SERIAL PRIMARY KEY,
                artist_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                album_name VARCHAR(255) NOT NULL,
                genre genre_enum NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT fk_artist
                    FOREIGN KEY (artist_id) 
                    REFERENCES artist(id)
                    ON DELETE CASCADE
            );
            """)
            print("Created Music Table")

        conn.commit()
