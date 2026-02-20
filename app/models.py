from app.db import get_connection
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor, execute_values
from app.utils.exceptions import ValidationError
from datetime import datetime


def dashboard_data():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""SELECT
        (SELECT COUNT(*) FROM users) AS total_users,
        (SELECT COUNT(*) FROM artist) AS total_artists,
        (SELECT COUNT(*) FROM music) AS total_music;""")
        data = cursor.fetchone()
        return data
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def register_user(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # check if email already exists
    cursor.execute("SELECT 1 FROM users WHERE email = %s", (data["email"],))
    if cursor.fetchone():
        raise ValidationError({"email": "Email already exists."})

    statement = """INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""
    try:
        cursor.execute(
            statement,
            (
                data["first_name"],
                data["last_name"],
                data["email"],
                generate_password_hash(data["password"]),
                data["phone"],
                data["dob"],
                data["gender"],
                data["address"],
                data["role"],
            ),
        )
        conn.commit()
        user_id = cursor.fetchone()["id"]
        return user_id
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def get_user_with_email(email: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_user_by_id(id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, first_name, last_name, email,password, phone, dob, gender, address, created_at, updated_at, role  FROM users WHERE id = %s",
        (id,),
    )
    result = cursor.fetchone()
    return result


def fetch_list_users(page: int = 1, page_size: int = 10):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        offset = (page - 1) * page_size

        cursor.execute("SELECT COUNT(*) as total FROM users")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT id, first_name, last_name, email, phone, dob, gender, 
                   address, created_at, updated_at, role 
            FROM users 
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (page_size, offset),
        )
        users = cursor.fetchall()

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        cursor.close()


def update_user(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # check if email already exists
    cursor.execute(
        "SELECT 1 FROM users WHERE email = %s AND id != %s", (data["email"], data["id"])
    )
    if cursor.fetchone():
        raise ValidationError({"email": "Email already exists."})

    statement = """UPDATE users set first_name=%s, last_name = %s, email= %s, phone= %s, dob = %s, gender = %s, address = %s, role = %s, updated_at=%s where id = %s"""
    try:
        cursor.execute(
            statement,
            (
                data["first_name"],
                data["last_name"],
                data["email"],
                data["phone"],
                data["dob"],
                data["gender"],
                data["address"],
                data["role"],
                datetime.now(),
                data["id"],
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise ValueError("User not found")

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise ValueError("No user was deleted")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


# artist section
def fetch_list_artist(page: int = 1, page_size: int = 10):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        offset = (page - 1) * page_size

        cursor.execute("SELECT COUNT(*) as total FROM artist")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT id, name, dob, gender, address, first_release_year, 
                   created_at, updated_at 
            FROM artist 
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (page_size, offset),
        )
        artists = cursor.fetchall()

        return {
            "artists": artists,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        cursor.close()


def get_all_artists():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("""
            SELECT name, dob, gender, address,
                   first_release_year, no_of_albums
            FROM artist
            ORDER BY name;
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_artist(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    statement = """INSERT INTO artist (name, dob, gender, address, first_release_year, no_of_albums, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;"""
    try:
        cursor.execute(
            statement,
            (
                data["name"],
                data["dob"],
                data["gender"],
                data["address"],
                data.get("first_release_year"),
                data.get("no_of_albums"),
                data.get("user_id"),
            ),
        )
        user_id = cursor.fetchone()["id"]
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def create_artists_bulk(data_list: list[dict]):
    conn = get_connection()
    cursor = conn.cursor()

    statement = """
        INSERT INTO artist 
        (name, dob, gender, address, first_release_year, no_of_albums)
        VALUES %s
        RETURNING id;
    """

    values = [
        (
            data["name"],
            data["dob"],
            data["gender"],
            data["address"],
            data["first_release_year"],
            data["no_of_albums"],
        )
        for data in data_list
    ]

    try:
        execute_values(cursor, statement, values)
        ids = cursor.fetchall()
        conn.commit()
        return ids

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def get_artist_by_id(id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, dob, gender, address, created_at, updated_at, first_release_year, no_of_albums, user_id  FROM artist WHERE id = %s",
        (id,),
    )
    result = cursor.fetchone()
    return result


def get_artist_by_user_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, dob, gender, address, created_at, updated_at, first_release_year, no_of_albums  FROM artist WHERE user_id = %s",
        (user_id,),
    )
    result = cursor.fetchone()
    return result


def update_artist(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    statement = """UPDATE artist set name=%s, dob = %s, gender = %s, address = %s, first_release_year = %s, no_of_albums=%s , updated_at=%s where id = %s"""
    try:
        cursor.execute(
            statement,
            (
                data["name"],
                data["dob"],
                data["gender"],
                data["address"],
                data["first_release_year"],
                data["no_of_albums"],
                datetime.now(),
                data["id"],
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def delete_artist(artist_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM artist WHERE id = %s", (artist_id,))
        if not cursor.fetchone():
            raise ValueError("Artist not found")

        cursor.execute("DELETE FROM artist WHERE id = %s", (artist_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise ValueError("No artist was deleted")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


# music section
def fetch_list_music(artist_id: int, page: int = 1, page_size: int = 10):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        offset = (page - 1) * page_size

        cursor.execute(
            "SELECT COUNT(*) as total FROM music where artist_id=%s", (artist_id,)
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT id, artist_id, title, album_name, genre, 
                   created_at, updated_at 
            FROM music WHERE artist_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (artist_id, page_size, offset),
        )
        musics = cursor.fetchall()

        return {
            "musics": musics,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        cursor.close()


def get_music_by_id(id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, artist_id, title, album_name, genre, created_at, updated_at FROM music WHERE id = %s",
        (id,),
    )
    result = cursor.fetchone()
    return result


def create_music(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    statement = """INSERT INTO music (artist_id, title, album_name, genre)
        VALUES (%s, %s, %s, %s) RETURNING id;"""
    try:
        cursor.execute(
            statement,
            (
                data["artist_id"],
                data["title"],
                data["album_name"],
                data["genre"],
            ),
        )
        record_id = cursor.fetchone()["id"]
        conn.commit()
        return record_id
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def update_music(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    statement = """UPDATE music set artist_id=%s, title = %s, album_name = %s, genre = %s, updated_at=%s where id = %s"""
    try:
        cursor.execute(
            statement,
            (
                data["artist_id"],
                data["title"],
                data["album_name"],
                data["genre"],
                datetime.now(),
                data["id"],
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def delete_music(music_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM music WHERE id = %s", (music_id,))
        if not cursor.fetchone():
            raise ValueError("Music not found")

        cursor.execute("DELETE FROM music WHERE id = %s", (music_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise ValueError("No Music was deleted")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
