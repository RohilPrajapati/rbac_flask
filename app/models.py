from app.db import get_connection
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor, execute_values
from app.utils.exceptions import ValidationError
from datetime import datetime


def dashboard_data():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM users) AS total_users,
                    (SELECT COUNT(*) FROM artist) AS total_artists,
                    (SELECT COUNT(*) FROM music) AS total_music;
            """)
            return cursor.fetchone()


def register_user(data: dict):
    with get_connection() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT 1 FROM users WHERE email = %s", (data["email"],))

                if cursor.fetchone():
                    raise ValidationError({"email": "Email already exists."})

                cursor.execute(
                    """
                    INSERT INTO users
                    (first_name, last_name, email, password, phone, dob, gender, address, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
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

                user_id = cursor.fetchone()["id"]
                conn.commit()
                return user_id

        except Exception:
            conn.rollback()
            raise


def get_user_with_email(email: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, first_name, last_name, email, password,
                       phone, dob, gender, address,
                       created_at, updated_at, role
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()


def fetch_list_users(page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM users")
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


def update_user(data: dict):
    with get_connection() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if email already exists for another user
                cursor.execute(
                    "SELECT 1 FROM users WHERE email = %s AND id != %s",
                    (data["email"], data["id"]),
                )
                if cursor.fetchone():
                    raise ValidationError({"email": "Email already exists."})

                cursor.execute(
                    """
                    UPDATE users
                    SET first_name = %s,
                        last_name = %s,
                        email = %s,
                        phone = %s,
                        dob = %s,
                        gender = %s,
                        address = %s,
                        role = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        data["first_name"],
                        data["last_name"],
                        data["email"],
                        data["phone"],
                        data["dob"],
                        data["gender"],
                        data["address"],
                        data["role"],
                        data["id"],
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError("User not found")

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise


def delete_user(user_id: int):
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,),
                )

                if cursor.rowcount == 0:
                    raise ValueError("User not found")

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise


# artist section
def fetch_list_artist(page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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


def get_all_artists():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT name, dob, gender, address,
                       first_release_year, no_of_albums
                FROM artist
                ORDER BY name;
            """)
            return cursor.fetchall()


def create_artist(data: dict):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            statement = """
                INSERT INTO artist
                (name, dob, gender, address, first_release_year, no_of_albums, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
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
            artist_id = cursor.fetchone()["id"]
            conn.commit()
            return artist_id


def create_artists_bulk(data_list: list[dict]):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
                    data.get("first_release_year"),
                    data.get("no_of_albums"),
                )
                for data in data_list
            ]
            execute_values(cursor, statement, values)
            ids = [row["id"] for row in cursor.fetchall()]
            conn.commit()
            return ids


def get_artist_by_id(id: int):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, name, dob, gender, address,
                       created_at, updated_at, first_release_year,
                       no_of_albums, user_id
                FROM artist
                WHERE id = %s
                """,
                (id,),
            )
            result = cursor.fetchone()
    return result


def get_artist_by_user_id(user_id: int):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, name, dob, gender, address,
                       created_at, updated_at, first_release_year, no_of_albums
                FROM artist
                WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()
    return result


def update_artist(data: dict):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            statement = """
                UPDATE artist
                SET name=%s,
                    dob=%s,
                    gender=%s,
                    address=%s,
                    first_release_year=%s,
                    no_of_albums=%s,
                    updated_at=%s
                WHERE id=%s
            """
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


def delete_artist(artist_id: int):
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
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


# music section


def fetch_list_music(artist_id: int, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT COUNT(*) as total FROM music WHERE artist_id = %s", (artist_id,)
            )
            total = cursor.fetchone()["total"]

            cursor.execute(
                """
                SELECT id, artist_id, title, album_name, genre,
                       created_at, updated_at
                FROM music
                WHERE artist_id = %s
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


def get_music_by_id(id: int):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, artist_id, title, album_name, genre, created_at, updated_at
                FROM music
                WHERE id = %s
                """,
                (id,),
            )
            result = cursor.fetchone()
    return result


def create_music(data: dict):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            statement = """
                INSERT INTO music (artist_id, title, album_name, genre)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """
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


def update_music(data: dict):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            statement = """
                UPDATE music 
                SET artist_id=%s, title=%s, album_name=%s, genre=%s, updated_at=%s
                WHERE id=%s
            """
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


def delete_music(music_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM music WHERE id = %s", (music_id,))
            if not cursor.fetchone():
                raise ValueError("Music not found")

            cursor.execute("DELETE FROM music WHERE id = %s", (music_id,))
            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError("No music was deleted")
