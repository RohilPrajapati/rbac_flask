from app.db import get_connection
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor
from app.utils.exceptions import ValidationError


def register_user(data: dict):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # check if email already exists
    cursor.execute("SELECT 1 FROM users WHERE email = %s", (data["email"],))
    if cursor.fetchone():
        cursor.close()
        conn.close()
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
        user_id = cursor.fetchone()["id"]
        conn.commit()
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
        "SELECT id, first_name, last_name, email,password, phone, dob, gender, address, created_at, updated_at, role  FROM users WHERE id = %d",
        (id,),
    )
    result = cursor.fetchone()
    return result


def fetch_list_users(page: int = 1, page_size: int = 10): ...
