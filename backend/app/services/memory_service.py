import json
from sqlalchemy import text
from app.db.connection import engine


def load_user_memory(user_id: int) -> dict:
    sql = text("""
        SELECT last_context
        FROM user_memory
        WHERE user_id = :uid
    """)

    with engine.connect() as conn:
        row = conn.execute(sql, {"uid": user_id}).mappings().first()

    if not row or not row["last_context"]:
        return {}

    try:
        return json.loads(row["last_context"])
    except Exception:
        return {}


def save_user_memory(user_id: int, context: dict):
    sql = text("""
        INSERT INTO user_memory (user_id, last_context)
        VALUES (:uid, :ctx)
        ON CONFLICT (user_id)
        DO UPDATE SET
            last_context = :ctx,
            updated_at = CURRENT_TIMESTAMP
    """)

    with engine.begin() as conn:
        conn.execute(
            sql,
            {
                "uid": user_id,
                "ctx": json.dumps(context),
            },
        )
