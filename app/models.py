from app.db import get_connection
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor
from app.utils.exceptions import ValidationError
from datetime import datetime


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
