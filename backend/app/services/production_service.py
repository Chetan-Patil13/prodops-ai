from sqlalchemy import text
from app.db.connection import engine


def get_daily_production_summary(line_code: str, date: str):
    """
    Returns total good & reject quantity for a line on a given date.
    """
    sql = text("""
        SELECT
            pl.line_code,
            DATE(p.event_time) AS production_date,
            SUM(p.quantity_good) AS total_good,
            SUM(p.quantity_reject) AS total_reject
        FROM production_log p
        JOIN production_lines pl ON p.line_id = pl.id
        WHERE pl.line_code = :line_code
          AND DATE(p.event_time) = :prod_date
        GROUP BY pl.line_code, DATE(p.event_time);
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {"line_code": line_code, "prod_date": date}
        ).mappings().first()

    return result
