from sqlalchemy import text
from app.db.connection import engine


def authenticate_user(email: str):
    sql = text("""
        SELECT
            u.id,
            u.user_email,
            u.full_name,
            ARRAY_AGG(r.role_name) AS roles
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
        WHERE u.user_email = :email
          AND u.is_active = TRUE
        GROUP BY u.id;
    """)

    with engine.connect() as conn:
        user = conn.execute(sql, {"email": email}).mappings().first()

    return user
