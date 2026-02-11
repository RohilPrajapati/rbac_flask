import psycopg2
from app.config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255),
        phone VARCHAR(20),
        dob DATE,
        gender gender_enum,
        address VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        role user_role
    );
    """)

    # --- Artist table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artist (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        dob DATE,
        gender gender_enum,
        address VARCHAR(255),
        first_release_year SMALLINT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """)

    # --- Music table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS music (
        id SERIAL PRIMARY KEY,
        artist_id int,
        title VARCHAR(255),
        album_name VARCHAR(255),
        genre genre_enum,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
